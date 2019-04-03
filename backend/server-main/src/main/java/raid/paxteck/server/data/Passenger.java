package raid.paxteck.server.data;

import javax.persistence.*;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

@Entity
@Table(name="passengers")
public class Passenger {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long id;

    @ElementCollection
    @CollectionTable(
            name = "passenger_interests",
            joinColumns = @JoinColumn(name="passenger_id")
    )
    private List<String> interests = new ArrayList<>();

    @Column(name="seat")
    private String assignedSeat;

    public Passenger() {
    }

    public long getId() {
        return id;
    }

    public void addInterest(String interest) {
        interests.add(interest);
    }

    public void addInterests(Collection<String> interest) {
        interests.addAll(interest);
    }

    public List<String> getInterests() {
        return Collections.unmodifiableList(interests);
    }

    public String getAssignedSeat() {
        return assignedSeat;
    }

    public void setAssignedSeat(String assignedSeat) {
        this.assignedSeat = assignedSeat;
    }
}
