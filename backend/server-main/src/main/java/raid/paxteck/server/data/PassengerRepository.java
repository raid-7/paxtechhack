package raid.paxteck.server.data;

import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface PassengerRepository extends CrudRepository<Passenger, Long> {

    Iterable<Passenger> getPassengersBySeat(String seat);

}
