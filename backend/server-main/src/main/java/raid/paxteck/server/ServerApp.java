package raid.paxteck.server;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.jdbc.datasource.DriverManagerDataSource;

import javax.sql.DataSource;

@SpringBootApplication
public class ServerApp {
    private static final String JDBC_URL_VAR = "db_url";
    private static final String JDBC_USER_VAR = "db_user";
    private static final String JDBC_PASSWORD_VAR = "db_password";

    @Bean
    public DataSource getDataSource() {
        DriverManagerDataSource dataSource = new DriverManagerDataSource();
        if (isEnvironmentConfigurationProvided()) {
            dataSource.setUrl(System.getenv(JDBC_URL_VAR));
            dataSource.setUsername(System.getenv(JDBC_USER_VAR));
            dataSource.setPassword(System.getenv(JDBC_PASSWORD_VAR));
        } else {
            dataSource.setUrl("jdbc:h2:file:./pax-test;DB_CLOSE_DELAY=-1");
        }
        return dataSource;
    }

    private boolean isEnvironmentConfigurationProvided() {
        return System.getenv(JDBC_URL_VAR) != null;
    }

    public static void main(String[] args) {
        SpringApplication.run(ServerApp.class, args);
    }

}
