package raid.paxteck.server.netinfo;

import java.util.List;

public class SeatResponse {
    private String seat;
    private List<PassengerInfo> neighbors;

    public SeatResponse() {
    }

    public SeatResponse(String seat, List<PassengerInfo> neighbors) {
        this.seat = seat;
        this.neighbors = neighbors;
    }

    public String getSeat() {
        return seat;
    }

    public List<PassengerInfo> getNeighbors() {
        return neighbors;
    }
}
