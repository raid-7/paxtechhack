package raid.paxteck.server;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import raid.paxteck.server.data.Passenger;
import raid.paxteck.server.data.PassengerRepository;

import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

@RestController
public class UtilityController {
    private final PassengerRepository repo;

    @Autowired
    public UtilityController(PassengerRepository repo) {
        this.repo = repo;
    }

    @GetMapping("reserved_seats_list")
    public List<String> getReservedSeats() {
        return StreamSupport.stream(repo.findAll().spliterator(), false)
                .map(Passenger::getSeat)
                .filter(Objects::nonNull)
                .collect(Collectors.toList());
    }
}
