# GitHub Copilot Instructions for Spring PetClinic

## Project Overview

This is the **Spring PetClinic** sample application - a Spring Boot application demonstrating best practices for building Java web applications. It uses Thymeleaf for templating, Spring Data JPA for persistence, and supports multiple databases (H2, MySQL, PostgreSQL).

## Technology Stack

- **Java 17+** (required)
- **Spring Boot 4.0.x**
- **Build Tools**: Maven (primary) and Gradle
- **Template Engine**: Thymeleaf
- **Persistence**: Spring Data JPA with Hibernate
- **Databases**: H2 (default), MySQL, PostgreSQL
- **CSS Framework**: Bootstrap 5.3.x (compiled from SCSS)
- **Testing**: JUnit 5, Testcontainers, Spring Boot Test

## Project Structure

```
src/
├── main/
│   ├── java/org/springframework/samples/petclinic/
│   │   ├── owner/          # Owner and Pet management
│   │   ├── vet/            # Veterinarian management
│   │   ├── visit/          # Visit management
│   │   └── system/         # System configuration (caching, etc.)
│   ├── resources/
│   │   ├── db/             # Database scripts
│   │   ├── messages/       # i18n message bundles
│   │   ├── templates/      # Thymeleaf templates
│   │   └── static/         # Static resources (CSS, images)
│   └── scss/               # SCSS source files
└── test/
    └── java/               # Test classes
```

## Code Style Guidelines

### Formatting
- Use **Spring Java Format** - the project enforces this via `spring-javaformat-maven-plugin`
- Run `./mvnw spring-javaformat:apply` to auto-format code
- Checkstyle is configured via `src/checkstyle/`

### Naming Conventions
- Entity classes: Singular nouns (e.g., `Owner`, `Pet`, `Vet`)
- Repository interfaces: `<Entity>Repository`
- Controller classes: `<Entity>Controller`
- Use `@Table(name = "table_name")` for JPA entities

### Spring Conventions
- Use constructor injection over field injection
- Annotate service classes with `@Service`
- Annotate repository interfaces with `@Repository`
- Use `@Transactional` for service methods that modify data

## Build Commands

### Maven (Preferred)
```bash
./mvnw spring-boot:run              # Run the application
./mvnw test                         # Run tests
./mvnw package                      # Build JAR
./mvnw spring-boot:build-image      # Build container image
./mvnw package -P css               # Compile SCSS to CSS
./mvnw spring-javaformat:apply      # Format code
```

### Gradle
```bash
./gradlew bootRun                   # Run the application
./gradlew test                      # Run tests
./gradlew build                     # Build JAR
```

## Database Profiles

- **Default (H2)**: No profile needed, in-memory database
- **MySQL**: `spring.profiles.active=mysql`
- **PostgreSQL**: `spring.profiles.active=postgres`

Use Docker Compose for local database instances:
```bash
docker compose up mysql      # Start MySQL
docker compose up postgres   # Start PostgreSQL
```

## Testing Guidelines

- Use `@SpringBootTest` for integration tests
- Use `@WebMvcTest` for controller tests
- Use `@DataJpaTest` for repository tests
- Testcontainers are configured for MySQL integration tests
- Docker Compose is used for PostgreSQL integration tests

### Test Application Classes
- `PetClinicIntegrationTests` - H2 database tests
- `MySqlTestApplication` - MySQL with Testcontainers
- `PostgresIntegrationTests` - PostgreSQL with Docker Compose

## Common Patterns

### Controller Pattern
```java
@Controller
class ExampleController {
    private final ExampleRepository repository;
    
    public ExampleController(ExampleRepository repository) {
        this.repository = repository;
    }
    
    @GetMapping("/example")
    public String list(Model model) {
        model.addAttribute("examples", repository.findAll());
        return "example/list";
    }
}
```

### Entity Pattern
```java
@Entity
@Table(name = "examples")
public class Example extends BaseEntity {
    @Column(name = "name")
    @NotBlank
    private String name;
    
    // Getters and setters
}
```

### Repository Pattern
```java
public interface ExampleRepository extends Repository<Example, Integer> {
    @Query("SELECT e FROM Example e WHERE e.name LIKE :name%")
    Collection<Example> findByName(@Param("name") String name);
    
    void save(Example example);
}
```

## Thymeleaf Templates

- Templates are located in `src/main/resources/templates/`
- Use layout fragments from `fragments/layout.html`
- Use `th:field` for form binding
- Use `th:errors` for validation error display

## Dependencies to Prefer

- Use Spring Boot starters over individual dependencies
- Use `javax.cache:cache-api` with Caffeine for caching
- Use Bean Validation annotations (`@NotBlank`, `@NotEmpty`, etc.)
- Use Webjars for frontend libraries

## Security Notes

- The application does not include Spring Security by default
- H2 console is exposed at `/h2-console` (development only)
- Validate all user input using Bean Validation

## Contributing

- All commits must include a **Signed-off-by** trailer (DCO)
- Follow the editor config settings in `.editorconfig`
- Ensure code passes checkstyle and format validation before committing
