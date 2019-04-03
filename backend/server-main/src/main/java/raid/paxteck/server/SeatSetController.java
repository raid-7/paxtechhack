package raid.paxteck.server;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.JSONValue;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import raid.paxteck.server.data.Passenger;
import raid.paxteck.server.data.PassengerRepository;
import raid.paxteck.server.netinfo.PassengerInfo;
import raid.paxteck.server.netinfo.SeatResponse;

import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.logging.Logger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@RestController
public class SeatSetController {
    public static boolean clearAllPassengersFlag = false;

    private final PassengerRepository repo;
    private final Pattern seatPattern = Pattern.compile("(\\d+)([a-zA-Z])");

    @Autowired
    public SeatSetController(PassengerRepository repo) {
        this.repo = repo;
        if (clearAllPassengersFlag) {
            clearAllPassengersFlag = false;
            repo.deleteAll();
        }
    }

    @PostMapping(value = "/request_seat", consumes = "application/json")
    public SeatResponse registerNextPassenger(@RequestBody PassengerInfo info) {
        Passenger passenger = new Passenger();
        passenger.addInterests(info.getInterests());
        passenger = repo.save(passenger);

        String seat = runSeatMatchingAlgorithm(passenger.getId());
        passenger.setAssignedSeat(seat);
        repo.save(passenger);
        List<Passenger> neighbors = getNeighbors(seat);

        return new SeatResponse(seat, neighbors.stream()
                .map(p -> new PassengerInfo(p.getInterests(), p.getAssignedSeat()))
                .collect(Collectors.toList())
        );
    }

    @PostMapping(value = "/clear_all")
    public void clearAll() {
        repo.deleteAll();
    }

    @GetMapping("/consistency_check")
    public String checkAll() {
        List<Passenger> passengers = new ArrayList<>();
        Set<String> seats = new HashSet<>();
        for (Passenger p : passengers) {
            String seat = p.getAssignedSeat();
            if (seat == null)
                continue;

            if (!seats.add(seat)) {
                // fatal
                return "FATAL\n" + seat;
            }
        }

        return "CONSISTENT";
    }

    private List<Passenger> getNeighbors(String seat) {
        List<Passenger> res = new ArrayList<>();
        for (Passenger p : repo.findAll()) {
            if (areSeatsNear(p.getAssignedSeat(), seat))
                res.add(p);
        }
        return res;
    }

    @SuppressWarnings("ResultOfMethodCallIgnored")
    private boolean areSeatsNear(String seatA, String seatB) {
        if (seatA == null || seatB == null)
            return false;
        if (seatA.equalsIgnoreCase(seatB))
            return false;

        Matcher matcherA = seatPattern.matcher(seatA.trim());
        matcherA.matches();
        Matcher matcherB = seatPattern.matcher(seatB.trim());
        matcherB.matches();
        long numericA = Integer.parseInt(matcherA.group(1));
        long numericB = Integer.parseInt(matcherB.group(1));
        char letterA = matcherA.group(2).toLowerCase().charAt(0);
        char letterB = matcherB.group(2).toLowerCase().charAt(0);
        return numericA == numericB &&
                (Math.max(letterA, letterB) <= 'C' || Math.min(letterA, letterB) > 'C');
    }

    @SuppressWarnings("unchecked")
    private String runSeatMatchingAlgorithm(long id) {
        JSONObject passengers = new JSONObject();
        for (Passenger p : repo.findAll()) {
            JSONArray interests = new JSONArray();
            interests.addAll(p.getInterests());
            JSONObject passengerJson = new JSONObject();
            passengerJson.put("interests", interests);
            if (p.getAssignedSeat() != null)
                passengerJson.put("seat", p.getAssignedSeat());
            passengers.put(String.valueOf(p.getId()), passengerJson);
        }

        for (int anonCount = 6 - passengers.size() % 6, i =0; i < anonCount; ++i) {
            JSONObject passengerJson = new JSONObject();
            passengerJson.put("interests", new JSONArray());
            passengers.put("__" + i, passengerJson);
        }


        Logger.getLogger(getClass().getName()).info(passengers.toJSONString());

        var controller = new ExecutionController("python3", "generator.py", "--stdin");
        PrintWriter out = controller.openOutput();
        out.println(passengers.toJSONString());
        out.close();

        try {
            controller.join();
        } catch (InterruptedException e) {
            throw new RuntimeException("Unexpected InterruptedException", e);
        }

        String resJson = new String(controller.getStdout(), StandardCharsets.UTF_8);
        String stderr = new String(controller.getStdout(), StandardCharsets.UTF_8);
        JSONObject resObj = (JSONObject) JSONValue.parse(resJson);

        Logger.getLogger(getClass().getName()).info(resJson);
        Logger.getLogger(getClass().getName()).warning(stderr);

        return String.valueOf(resObj.get(String.valueOf(id)));
    }
}
