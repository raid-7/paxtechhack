package raid.paxteck.server.data;

import javax.persistence.*;
import java.util.Collection;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Entity
@Table(name="passengers")
public class Passenger {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long id;

    @Column(name="interests")
    private String interests;

    @Column(name="seat")
    private String seat;

    public Passenger() {
    }

    public long getId() {
        return id;
    }

    public void addInterest(String interest) {
        addInterests(List.of(interest));
    }

    public void addInterests(Collection<String> othInterests) {
        Set<String> setInterests = new HashSet<>(getInterests());
        setInterests.addAll(othInterests);
        interests = String.join(",", setInterests);
    }

    public Set<String> getInterests() {
        return interests == null ? Set.of() : Set.of(interests.split(","));
    }

    public String getSeat() {
        return seat;
    }

    public void setSeat(String seat) {
        this.seat = seat;
    }
}
