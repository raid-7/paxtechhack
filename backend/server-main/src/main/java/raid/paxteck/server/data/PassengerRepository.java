package raid.paxteck.server.data;

import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PassengerRepository extends CrudRepository<Passenger, Long> {

    List<Passenger> getPassengersBySeat(String seat);

}
