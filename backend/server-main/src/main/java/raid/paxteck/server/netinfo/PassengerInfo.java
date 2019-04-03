package raid.paxteck.server.netinfo;

import java.util.List;

public class PassengerInfo {
    private String assignedSeat;
    private List<String> interests;

    public PassengerInfo() {
    }

    public PassengerInfo(List<String> interests, String assignedSeat) {
        this.assignedSeat = assignedSeat;
        this.interests = interests;
    }

    public PassengerInfo(List<String> interests) {
        this(interests, null);
    }

    public String getAssignedSeat() {
        return assignedSeat;
    }

    public List<String> getInterests() {
        return interests;
    }
}
