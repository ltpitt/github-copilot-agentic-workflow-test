# Package: org.springframework.samples.petclinic.vet

## Overview

The `vet` package manages veterinarian information in the PetClinic application. It provides functionality for displaying veterinarians and their specialties, with support for paginated web views and RESTful JSON/XML endpoints. The package leverages JCache caching for performance optimization and implements Spring Data JPA for persistence.

**Key Capabilities:**
- Veterinarian and specialty entity management with JPA
- Paginated web interface for browsing veterinarians
- RESTful API endpoints (JSON/XML) for vet data access
- Many-to-many relationship between vets and specialties
- JCache integration for optimized data retrieval
- JAXB support for XML marshalling

---

## Architecture

### Entity Model

```
BaseEntity (model package)
    ├── Person (model package)
    │   └── Vet
    └── NamedEntity (model package)
        └── Specialty
```

### Database Schema

**Tables:**
- `vets` - Veterinarian information (id, first_name, last_name)
- `specialties` - Specialty types (id, name)
- `vet_specialties` - Join table for many-to-many relationship

**Relationships:**
- Vet ↔ Specialty: Many-to-Many (eager fetch)
- Join table: `vet_specialties` (vet_id, specialty_id)

---

## Classes

### 1. Vet (Entity)

**Location:** `org.springframework.samples.petclinic.vet.Vet`

**Purpose:** JPA entity representing a veterinarian in the PetClinic system. Extends `Person` to inherit first name and last name properties.

**Inheritance Hierarchy:**
```
BaseEntity → Person → Vet
```

**Database Mapping:**
- **Table:** `vets`
- **Columns:** `id` (inherited), `first_name` (inherited), `last_name` (inherited)

**Key Fields:**

| Field | Type | Annotations | Description |
|-------|------|-------------|-------------|
| `specialties` | `Set<Specialty>` | `@ManyToMany(fetch = FetchType.EAGER)` | Vet's medical specialties |

**Key Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `getSpecialties()` | `List<Specialty>` | Returns sorted list of specialties (annotated with `@XmlElement` for JAXB) |
| `getSpecialtiesInternal()` | `Set<Specialty>` | Protected accessor for internal set management |
| `getNrOfSpecialties()` | `int` | Returns count of specialties |
| `addSpecialty(Specialty)` | `void` | Adds a specialty to the vet |

**Relationship Configuration:**
```java
@ManyToMany(fetch = FetchType.EAGER)
@JoinTable(
    name = "vet_specialties",
    joinColumns = @JoinColumn(name = "vet_id"),
    inverseJoinColumns = @JoinColumn(name = "specialty_id")
)
private Set<Specialty> specialties;
```

**Design Notes:**
- Uses **eager fetching** to avoid lazy-loading issues when serializing to JSON/XML
- Internal `Set` is exposed as sorted `List` to provide consistent ordering
- Sorting is based on `NamedEntity::getName` using natural alphabetical order
- JAXB annotations (`@XmlElement`) enable XML serialization

**Example Usage:**
```java
Vet vet = new Vet();
vet.setFirstName("James");
vet.setLastName("Carter");

Specialty surgery = new Specialty();
surgery.setName("surgery");
vet.addSpecialty(surgery);

List<Specialty> specialties = vet.getSpecialties(); // Sorted list
int count = vet.getNrOfSpecialties(); // Returns 1
```

---

### 2. Specialty (Entity)

**Location:** `org.springframework.samples.petclinic.vet.Specialty`

**Purpose:** JPA entity representing a veterinary specialty (e.g., dentistry, surgery, radiology). Simple entity that extends `NamedEntity` to inherit naming capabilities.

**Inheritance Hierarchy:**
```
BaseEntity → NamedEntity → Specialty
```

**Database Mapping:**
- **Table:** `specialties`
- **Columns:** `id` (inherited), `name` (inherited from NamedEntity)

**Inherited Properties:**
- `id` (Integer) - Primary key from `BaseEntity`
- `name` (String) - Specialty name from `NamedEntity` with `@NotBlank` validation

**Design Notes:**
- Minimal entity with no additional fields beyond inherited ones
- Uses `NamedEntity` base class for consistent naming across domain
- Referenced by `Vet` entities through many-to-many relationship
- Implements `toString()` via `NamedEntity` to return the specialty name

**Common Specialty Examples:**
- radiology
- surgery
- dentistry

---

### 3. Vets (DTO)

**Location:** `org.springframework.samples.petclinic.vet.Vets`

**Purpose:** Data Transfer Object (DTO) that wraps a list of `Vet` entities for XML/JSON serialization. Simplifies object-to-XML/JSON mapping in REST endpoints.

**JAXB Annotations:**
- `@XmlRootElement` - Marks class as XML root element
- `@XmlElement` on `getVetList()` - Defines XML element for the vet list

**Key Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `vets` | `List<Vet>` | List of veterinarian entities |

**Key Methods:**

| Method | Return Type | Description |
|--------|-------------|-------------|
| `getVetList()` | `List<Vet>` | Returns vet list, initializes empty ArrayList if null |

**Design Notes:**
- **Wrapper Pattern**: Encapsulates collection for cleaner marshalling
- Lazy initialization ensures non-null list is always returned
- Used by both XML views and JSON REST endpoints
- Simplifies JAXB binding configuration

**XML Serialization Example:**
```xml
<vets>
    <vetList>
        <vet>
            <id>1</id>
            <firstName>James</firstName>
            <lastName>Carter</lastName>
            <specialties>
                <specialty>
                    <id>1</id>
                    <name>radiology</name>
                </specialty>
            </specialties>
        </vet>
    </vetList>
</vets>
```

**JSON Serialization Example:**
```json
{
    "vetList": [
        {
            "id": 1,
            "firstName": "James",
            "lastName": "Carter",
            "specialties": [
                {
                    "id": 1,
                    "name": "radiology"
                }
            ]
        }
    ]
}
```

---

### 4. VetRepository (Repository Interface)

**Location:** `org.springframework.samples.petclinic.vet.VetRepository`

**Purpose:** Spring Data repository interface for `Vet` entity persistence and retrieval. Provides cached data access methods with transaction management.

**Inheritance:**
```
Repository<Vet, Integer> (Spring Data)
```

**Key Methods:**

| Method | Return Type | Annotations | Description |
|--------|-------------|-------------|-------------|
| `findAll()` | `Collection<Vet>` | `@Cacheable("vets")`, `@Transactional(readOnly = true)` | Retrieves all vets from database |
| `findAll(Pageable)` | `Page<Vet>` | `@Cacheable("vets")`, `@Transactional(readOnly = true)` | Retrieves paginated vets |

**Caching Strategy:**

Both methods use the **`@Cacheable("vets")`** annotation:
- **Cache Name:** `vets`
- **Implementation:** JCache (JSR-107) with Caffeine provider
- **Configuration:** Defined in `CacheConfiguration` class
- **Statistics:** Enabled via JMX for monitoring
- **Eviction:** Automatic based on Caffeine defaults

**Transaction Management:**
- All queries marked `@Transactional(readOnly = true)` for optimization
- Read-only hint allows database to optimize query execution
- No explicit write methods defined (Spring Data handles saves)

**Pagination Support:**
- Uses Spring Data's `Pageable` interface
- Returns `Page<Vet>` with metadata (total pages, elements, etc.)
- See `VetController.findPaginated()` for usage example

**Design Notes:**
- Extends Spring Data `Repository` interface (not `CrudRepository`)
- Methods follow Spring Data naming conventions
- Cache improves performance for frequently accessed vet lists
- Both paginated and non-paginated access supported

**Example Usage:**
```java
// Non-paginated
Collection<Vet> allVets = vetRepository.findAll();

// Paginated
Pageable pageable = PageRequest.of(0, 5); // Page 0, size 5
Page<Vet> page = vetRepository.findAll(pageable);
int totalPages = page.getTotalPages();
List<Vet> vets = page.getContent();
```

---

### 5. VetController (Controller)

**Location:** `org.springframework.samples.petclinic.vet.VetController`

**Purpose:** Spring MVC controller that handles HTTP requests for veterinarian data. Provides both web UI (HTML) and REST API (JSON/XML) endpoints.

**Annotations:**
- `@Controller` - Marks class as Spring MVC controller

**Dependencies:**

| Dependency | Type | Injection Method |
|------------|------|------------------|
| `vetRepository` | `VetRepository` | Constructor injection |

**Endpoints:**

#### 1. GET `/vets.html` - Paginated Web View

**Method:** `showVetList(@RequestParam(defaultValue = "1") int page, Model model)`

**Purpose:** Displays veterinarians in a paginated HTML table view

**Parameters:**
- `page` (optional) - Page number, defaults to 1

**Model Attributes:**
- `currentPage` - Current page number
- `totalPages` - Total number of pages
- `totalItems` - Total number of veterinarians
- `listVets` - List of vets for current page

**Returns:** `"vets/vetList"` (Thymeleaf template)

**Pagination Configuration:**
- **Page Size:** 5 vets per page
- **Index:** 1-based for user-facing URLs, 0-based internally

**Implementation Flow:**
```
1. Convert 1-based page to 0-based index
2. Create PageRequest with size 5
3. Fetch paginated data from repository
4. Populate Vets DTO with results
5. Add pagination metadata to model
6. Return template name
```

#### 2. GET `/vets` - REST API Endpoint

**Method:** `showResourcesVetList()`

**Purpose:** Returns all veterinarians as JSON or XML for API consumption

**Return Type:** `@ResponseBody Vets`

**Response Formats:**
- **JSON** (default)
- **XML** (via Accept header or .xml extension)

**Caching:** Leverages repository-level caching

**Design Notes:**
- Returns `Vets` DTO for simpler JSON/XML marshalling
- No pagination on REST endpoint (returns all vets)
- Content negotiation handled by Spring MVC

**Private Helper Methods:**

| Method | Purpose |
|--------|---------|
| `findPaginated(int page)` | Creates PageRequest and fetches page from repository |
| `addPaginationModel(int page, Page<Vet> paginated, Model model)` | Populates model with pagination data |

**Example Requests:**

```bash
# HTML view (page 1)
GET /vets.html

# HTML view (page 2)
GET /vets.html?page=2

# JSON response
GET /vets
Accept: application/json

# XML response
GET /vets
Accept: application/xml
```

**Example JSON Response:**
```json
{
  "vetList": [
    {
      "id": 1,
      "firstName": "James",
      "lastName": "Carter",
      "specialties": []
    },
    {
      "id": 2,
      "firstName": "Helen",
      "lastName": "Leary",
      "specialties": [
        {
          "id": 1,
          "name": "radiology"
        }
      ]
    }
  ]
}
```

---

## Entity Relationships

### Many-to-Many: Vet ↔ Specialty

```
┌─────────────┐              ┌──────────────────┐              ┌──────────────┐
│    Vet      │              │  vet_specialties │              │  Specialty   │
├─────────────┤              ├──────────────────┤              ├──────────────┤
│ id          │◄─────────────┤ vet_id           │              │ id           │
│ first_name  │              │ specialty_id     ├─────────────►│ name         │
│ last_name   │              └──────────────────┘              └──────────────┘
└─────────────┘
     1..*                                                             1..*
```

**Characteristics:**
- **Fetch Type:** EAGER (specialties loaded with vet)
- **Cascade:** None explicitly defined
- **Orphan Removal:** Not applicable
- **Bidirectional:** No (unidirectional from Vet side)

**Join Table Configuration:**
```java
@JoinTable(
    name = "vet_specialties",
    joinColumns = @JoinColumn(name = "vet_id"),
    inverseJoinColumns = @JoinColumn(name = "specialty_id")
)
```

---

## Caching Strategy

### JCache Configuration

**Cache Provider:** Caffeine (via JCache abstraction)

**Cache Definition:**
- **Name:** `"vets"`
- **Configuration Class:** `org.springframework.samples.petclinic.system.CacheConfiguration`
- **Statistics:** Enabled for JMX monitoring

**Configuration Details:**
```java
@Bean
public JCacheManagerCustomizer petclinicCacheConfigurationCustomizer() {
    return cm -> cm.createCache("vets", cacheConfiguration());
}

private Configuration<Object, Object> cacheConfiguration() {
    return new MutableConfiguration<>().setStatisticsEnabled(true);
}
```

**Cached Methods:**
1. `VetRepository.findAll()` - Caches complete vet list
2. `VetRepository.findAll(Pageable)` - Caches paginated results

**Cache Behavior:**
- **Cache Key:** Automatically generated by Spring (method parameters)
- **Eviction:** Managed by Caffeine (default settings)
- **TTL:** Not explicitly configured (uses Caffeine defaults)
- **Statistics:** Available via JMX MBeans

**Performance Impact:**
- Reduces database queries for frequently accessed vet lists
- Particularly beneficial for the `/vets` REST endpoint
- Eager loading of specialties happens once per cache entry

**Monitoring:**
Access cache statistics via JMX:
- Cache hits/misses
- Cache size
- Eviction count

---

## REST API Documentation

### Endpoint Overview

| Endpoint | Method | Content Type | Purpose |
|----------|--------|--------------|---------|
| `/vets` | GET | JSON/XML | Retrieve all veterinarians |
| `/vets.html` | GET | HTML | Display paginated vet list |

### API Endpoint: GET /vets

**Description:** Returns complete list of veterinarians with their specialties

**Request:**
```http
GET /vets HTTP/1.1
Host: localhost:8080
Accept: application/json
```

**Response (JSON):**
```json
{
  "vetList": [
    {
      "id": 1,
      "firstName": "James",
      "lastName": "Carter",
      "specialties": []
    },
    {
      "id": 2,
      "firstName": "Helen",
      "lastName": "Leary",
      "specialties": [
        {
          "id": 1,
          "name": "radiology"
        }
      ]
    },
    {
      "id": 3,
      "firstName": "Linda",
      "lastName": "Douglas",
      "specialties": [
        {
          "id": 2,
          "name": "surgery"
        },
        {
          "id": 3,
          "name": "dentistry"
        }
      ]
    }
  ]
}
```

**Response (XML):**
```http
GET /vets HTTP/1.1
Host: localhost:8080
Accept: application/xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<vets>
    <vetList>
        <id>1</id>
        <firstName>James</firstName>
        <lastName>Carter</lastName>
        <specialties/>
    </vetList>
    <vetList>
        <id>2</id>
        <firstName>Helen</firstName>
        <lastName>Leary</lastName>
        <specialties>
            <id>1</id>
            <name>radiology</name>
        </specialties>
    </vetList>
</vets>
```

**HTTP Status Codes:**
- `200 OK` - Successfully retrieved vet list
- `500 Internal Server Error` - Database or server error

**Caching:** Response data is cached at repository level

---

## XML/JSON Serialization

### JAXB Configuration

**Annotated Classes:**

1. **Vets DTO:**
   - `@XmlRootElement` - Defines root element for XML
   - `@XmlElement` on `getVetList()` - Maps method to XML element

2. **Vet Entity:**
   - `@XmlElement` on `getSpecialties()` - Maps specialties collection

**Serialization Flow:**

```
Controller (@ResponseBody)
    ↓
Vets DTO (wrapper)
    ↓
List<Vet> (entities)
    ↓
List<Specialty> (sorted collection)
    ↓
JSON/XML (via Jackson/JAXB)
```

### Content Negotiation

Spring MVC automatically selects serialization format based on:

1. **Accept Header:**
   - `application/json` → Jackson (JSON)
   - `application/xml` → JAXB (XML)

2. **URL Extension (if enabled):**
   - `/vets.json` → JSON
   - `/vets.xml` → XML

### Jackson Configuration

**Default Behavior:**
- Property-based serialization (uses getters)
- Null fields included by default
- Collections serialized as JSON arrays
- Specialties sorted alphabetically (via `getSpecialties()`)

**Customization Points:**
- Extend with `@JsonProperty`, `@JsonIgnore` if needed
- Configure global ObjectMapper in WebConfiguration

---

## Pagination Implementation

### Web UI Pagination

**Configuration:**
- **Page Size:** 5 vets per page (hardcoded in `VetController.findPaginated()`)
- **Page Numbering:** 1-based for users, 0-based internally
- **Default Page:** 1

**Controller Implementation:**

```java
private Page<Vet> findPaginated(int page) {
    int pageSize = 5;
    Pageable pageable = PageRequest.of(page - 1, pageSize);
    return vetRepository.findAll(pageable);
}
```

**Model Attributes:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `currentPage` | `int` | Active page number (1-based) |
| `totalPages` | `int` | Total number of pages |
| `totalItems` | `long` | Total number of veterinarians |
| `listVets` | `List<Vet>` | Vets for current page |

### Thymeleaf Template Integration

**Template:** `src/main/resources/templates/vets/vetList.html`

**Key Features:**

1. **Vet Table:**
```html
<tr th:each="vet : ${listVets}">
    <td th:text="${vet.firstName + ' ' + vet.lastName}"></td>
    <td>
        <span th:each="specialty : ${vet.specialties}" 
              th:text="${specialty.name + ' '}" />
        <span th:if="${vet.nrOfSpecialties == 0}" 
              th:text="#{none}">none</span>
    </td>
</tr>
```

2. **Pagination Controls:**
   - Page number links (1, 2, 3, ...)
   - First/Previous/Next/Last navigation
   - Current page highlighted
   - Disabled navigation when at boundaries

**Navigation URLs:**
```
/vets.html?page=1     (First page)
/vets.html?page=2     (Second page)
/vets.html?page=N     (Page N)
```

**Pagination Logic:**
- Display pagination only if `totalPages > 1`
- Current page not clickable
- Navigation buttons disabled at boundaries
- Font Awesome icons for navigation (`fa-fast-backward`, etc.)

---

## Usage Examples

### Example 1: Fetching All Vets (Service Layer)

```java
@Service
public class VetService {
    private final VetRepository vetRepository;
    
    public VetService(VetRepository vetRepository) {
        this.vetRepository = vetRepository;
    }
    
    public Collection<Vet> getAllVets() {
        // Cached query
        return vetRepository.findAll();
    }
    
    public List<Vet> getVetsWithSpecialty(String specialtyName) {
        return vetRepository.findAll().stream()
            .filter(vet -> vet.getSpecialties().stream()
                .anyMatch(s -> s.getName().equals(specialtyName)))
            .collect(Collectors.toList());
    }
}
```

### Example 2: Creating a New Vet (Hypothetical)

```java
@Transactional
public void createVet(String firstName, String lastName, List<String> specialtyNames) {
    Vet vet = new Vet();
    vet.setFirstName(firstName);
    vet.setLastName(lastName);
    
    // Add specialties
    for (String name : specialtyNames) {
        Specialty specialty = specialtyRepository.findByName(name);
        if (specialty != null) {
            vet.addSpecialty(specialty);
        }
    }
    
    vetRepository.save(vet);
}
```

### Example 3: REST Client Consuming JSON

```javascript
// Fetch all vets via REST API
fetch('/vets', {
    headers: {
        'Accept': 'application/json'
    }
})
.then(response => response.json())
.then(data => {
    data.vetList.forEach(vet => {
        console.log(`${vet.firstName} ${vet.lastName}`);
        vet.specialties.forEach(s => {
            console.log(`  - ${s.name}`);
        });
    });
});
```

### Example 4: Paginated Retrieval

```java
public Page<Vet> getVetPage(int pageNumber) {
    int pageSize = 5;
    Pageable pageable = PageRequest.of(pageNumber - 1, pageSize);
    Page<Vet> page = vetRepository.findAll(pageable);
    
    System.out.println("Page: " + (pageNumber));
    System.out.println("Total pages: " + page.getTotalPages());
    System.out.println("Total vets: " + page.getTotalElements());
    
    return page;
}
```

### Example 5: Testing with Specialties

```java
@Test
void testVetWithMultipleSpecialties() {
    Vet vet = new Vet();
    vet.setFirstName("Test");
    vet.setLastName("Vet");
    
    Specialty surgery = new Specialty();
    surgery.setName("surgery");
    
    Specialty dentistry = new Specialty();
    dentistry.setName("dentistry");
    
    vet.addSpecialty(surgery);
    vet.addSpecialty(dentistry);
    
    assertEquals(2, vet.getNrOfSpecialties());
    
    // Verify sorting
    List<Specialty> specialties = vet.getSpecialties();
    assertEquals("dentistry", specialties.get(0).getName());
    assertEquals("surgery", specialties.get(1).getName());
}
```

---

## Dependencies

### Internal Dependencies

| Package | Classes Used | Purpose |
|---------|-------------|---------|
| `org.springframework.samples.petclinic.model` | `Person`, `NamedEntity`, `BaseEntity` | Entity inheritance hierarchy |

### External Dependencies

| Dependency | Usage |
|------------|-------|
| `jakarta.persistence.*` | JPA annotations (@Entity, @Table, @ManyToMany, etc.) |
| `jakarta.xml.bind.annotation.*` | JAXB annotations (@XmlRootElement, @XmlElement) |
| `org.springframework.data.*` | Repository interfaces, Pageable, Page |
| `org.springframework.cache.annotation.*` | @Cacheable annotation |
| `org.springframework.stereotype.*` | @Controller annotation |
| `org.springframework.transaction.annotation.*` | @Transactional annotation |
| `org.springframework.web.bind.annotation.*` | @GetMapping, @ResponseBody, @RequestParam |

### Reverse Dependencies

Packages that depend on `vet`:
- None (vet package is self-contained)

---

## Architectural Notes

### Design Patterns

1. **Repository Pattern:**
   - `VetRepository` abstracts data access
   - Spring Data JPA provides implementation
   - Enables testability and loose coupling

2. **Data Transfer Object (DTO):**
   - `Vets` class wraps entity collection
   - Simplifies XML/JSON marshalling
   - Decouples API contract from domain model

3. **MVC Pattern:**
   - `VetController` handles HTTP requests
   - `Vet`/`Specialty` represent model
   - Thymeleaf templates provide view layer

4. **Lazy Initialization:**
   - `Vets.getVetList()` initializes on demand
   - `Vet.getSpecialtiesInternal()` ensures non-null collection

### Best Practices

1. **Constructor Injection:**
   - `VetController` uses constructor injection
   - Enables immutability and easier testing
   - Follows Spring Framework recommendations

2. **Read-Only Transactions:**
   - `@Transactional(readOnly = true)` on queries
   - Optimizes database performance
   - Signals intent clearly

3. **Eager Fetching:**
   - Specialties loaded with vets (`FetchType.EAGER`)
   - Prevents N+1 query problem in serialization
   - Trade-off: Slightly larger memory footprint

4. **Sorted Collections:**
   - Specialties returned in alphabetical order
   - Consistent user experience
   - Predictable JSON/XML output

5. **Caching:**
   - Repository-level caching reduces database load
   - Transparent to controller layer
   - Statistics enabled for monitoring

6. **Content Negotiation:**
   - Single endpoint supports JSON/XML
   - Leverages Spring MVC capabilities
   - Reduces code duplication

### Security Considerations

**Current State:**
- No authentication/authorization implemented
- All endpoints publicly accessible
- Read-only operations (safe from data modification)

**Future Enhancements:**
- Add Spring Security for authentication
- Implement role-based access control
- Consider rate limiting for REST API
- Add CORS configuration for cross-origin requests

### Performance Optimization

1. **Caching:**
   - JCache reduces repeated database queries
   - Particularly effective for reference data (vets change infrequently)

2. **Eager Loading:**
   - Avoids lazy-loading exceptions in serialization
   - Single query fetches vet + specialties

3. **Pagination:**
   - Limits result set size in web UI
   - Reduces memory consumption
   - Improves page load time

4. **Index Usage:**
   - Database indexes on `vets.last_name` and `specialties.name`
   - Improves query performance

### Testing Strategy

**Unit Testing:**
- Test entity methods (`Vet.addSpecialty()`, `getNrOfSpecialties()`)
- Test controller logic with mocked repository
- Verify pagination calculations

**Integration Testing:**
- Test repository queries with test database
- Verify caching behavior
- Test REST endpoint serialization

**Example Test:**
```java
@WebMvcTest(VetController.class)
class VetControllerTests {
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private VetRepository vetRepository;
    
    @Test
    void testShowVetList() throws Exception {
        mockMvc.perform(get("/vets.html"))
            .andExpect(status().isOk())
            .andExpect(view().name("vets/vetList"))
            .andExpect(model().attributeExists("listVets"));
    }
    
    @Test
    void testShowResourcesVetList() throws Exception {
        mockMvc.perform(get("/vets")
                .accept(MediaType.APPLICATION_JSON))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.vetList").isArray());
    }
}
```

---

## Future Enhancements

### Potential Improvements

1. **REST API Pagination:**
   - Add pagination support to `/vets` endpoint
   - Include HATEOAS links for navigation
   - Return total count in headers

2. **Search/Filter:**
   - Search vets by name
   - Filter by specialty
   - Advanced query support

3. **Write Operations:**
   - POST `/vets` - Create new vet
   - PUT `/vets/{id}` - Update vet
   - DELETE `/vets/{id}` - Delete vet
   - Manage vet-specialty associations

4. **Validation:**
   - Add Bean Validation annotations
   - Validate specialty assignments
   - Prevent duplicate specialties

5. **Caching Improvements:**
   - Configure TTL for cache entries
   - Add cache eviction on data modification
   - Implement cache warming strategy

6. **API Versioning:**
   - Version REST API endpoints
   - Support multiple API versions
   - Deprecation strategy

7. **Documentation:**
   - OpenAPI/Swagger documentation
   - API usage examples
   - Rate limiting documentation

---

## Related Documentation

- [Model Package Documentation](model.md) - Base entity classes
- [System Package Documentation](system.md) - Cache configuration
- [Owner Package Documentation](owner.md) - Similar entity management patterns

---

## References

### Spring Framework Documentation
- [Spring Data JPA Reference](https://docs.spring.io/spring-data/jpa/docs/current/reference/html/)
- [Spring MVC Documentation](https://docs.spring.io/spring-framework/docs/current/reference/html/web.html)
- [Spring Cache Abstraction](https://docs.spring.io/spring-framework/docs/current/reference/html/integration.html#cache)

### Java EE Specifications
- [Jakarta Persistence (JPA) 3.0](https://jakarta.ee/specifications/persistence/3.0/)
- [Jakarta XML Binding (JAXB) 3.0](https://jakarta.ee/specifications/xml-binding/3.0/)
- [JCache (JSR-107)](https://jcp.org/en/jsr/detail?id=107)

### Design Patterns
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Data Transfer Object](https://martinfowler.com/eaaCatalog/dataTransferObject.html)

---

**Last Updated:** 2026-01-09  
**Package Version:** Spring Boot 4.0.x  
**Maintainers:** Spring PetClinic Team
