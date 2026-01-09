# Package: org.springframework.samples.petclinic.owner

## Overview

The `owner` package is the core domain module of the PetClinic application, implementing comprehensive management of pet owners, their pets, and veterinary visits. It provides complete CRUD operations, search functionality with pagination, and form validation for all related entities. This package follows Spring MVC best practices with clear separation between domain models, data access repositories, web controllers, and supporting components.

## Architecture & Design Patterns

### Design Patterns Used
- **MVC (Model-View-Controller)**: Separates domain logic, data access, and presentation
- **Repository Pattern**: Data access abstraction via Spring Data JPA
- **Dependency Injection**: Constructor-based injection for all dependencies
- **Domain-Driven Design**: Rich domain model with entity relationships and business logic
- **Validator Pattern**: Custom validation for complex business rules
- **Formatter Pattern**: Type conversion for Spring MVC form binding

### Package Dependencies
- **Internal Dependencies**:
  - `org.springframework.samples.petclinic.model` - Base entities (BaseEntity, NamedEntity, Person)
- **External Dependencies**:
  - Spring Framework (Core, MVC, Data JPA)
  - Jakarta Persistence (JPA)
  - Jakarta Validation (Bean Validation)
  - Hibernate (JPA implementation)

---

## Entity Relationship Model

```
┌─────────────┐
│   Owner     │
│  (Person)   │ 1
└──────┬──────┘
       │
       │ owns
       │
       │ *
┌──────▼──────┐      ┌─────────────┐
│     Pet     │  *   │   PetType   │
│(NamedEntity)├──────►│(NamedEntity)│
└──────┬──────┘ has  └─────────────┘
       │
       │ has
       │
       │ *
┌──────▼──────┐
│    Visit    │
│(BaseEntity) │
└─────────────┘

Inheritance Hierarchy:
BaseEntity
├── NamedEntity
│   ├── Pet
│   └── PetType
└── Person
    └── Owner
```

### Relationship Details
- **Owner → Pet**: One-to-Many (bidirectional, cascade ALL, eager fetch)
- **Pet → PetType**: Many-to-One (no cascade)
- **Pet → Visit**: One-to-Many (bidirectional, cascade ALL, eager fetch)

---

## Classes

### 1. Owner (Entity)

**Purpose**: Represents a pet owner with contact information and pet management capabilities.

**Type**: `@Entity` mapped to `owners` table

**Inheritance**: Extends `Person` (inherits firstName, lastName, id)

**Key Fields**:
| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `address` | `String` | `@NotBlank` | Owner's street address |
| `city` | `String` | `@NotBlank` | Owner's city |
| `telephone` | `String` | `@NotBlank`, `@Pattern("\\d{10}")` | 10-digit phone number |
| `pets` | `List<Pet>` | `@OneToMany(cascade=ALL, fetch=EAGER)` | Owner's pets, ordered by name |

**Key Methods**:
| Method | Description |
|--------|-------------|
| `void addPet(Pet pet)` | Adds a new pet to the owner's collection (only if pet is new) |
| `Pet getPet(String name)` | Retrieves pet by name (case-insensitive) |
| `Pet getPet(Integer id)` | Retrieves pet by ID |
| `Pet getPet(String name, boolean ignoreNew)` | Retrieves pet by name with option to exclude unsaved pets |
| `void addVisit(Integer petId, Visit visit)` | Adds a visit to a specific pet (with validation) |

**JPA Annotations**:
- `@Entity` - Marks as JPA entity
- `@Table(name = "owners")` - Maps to owners table
- `@OneToMany` - Manages pet collection with cascade operations
- `@JoinColumn(name = "owner_id")` - Foreign key in pets table
- `@OrderBy("name")` - Pets sorted alphabetically

**Validation**:
- All personal fields are required (`@NotBlank`)
- Telephone must match 10-digit pattern
- Cascades validation to all pets

**Business Logic**:
- Prevents duplicate pet addition for existing pets
- Provides multiple lookup strategies for pets
- Validates pet and visit existence before operations
- Uses Spring's `ToStringCreator` for debugging output

---

### 2. Pet (Entity)

**Purpose**: Represents a pet belonging to an owner with medical visit history.

**Type**: `@Entity` mapped to `pets` table

**Inheritance**: Extends `NamedEntity` (inherits name, id)

**Key Fields**:
| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `birthDate` | `LocalDate` | `@DateTimeFormat("yyyy-MM-dd")` | Pet's date of birth |
| `type` | `PetType` | `@ManyToOne` | Type/species of pet (cat, dog, etc.) |
| `visits` | `Set<Visit>` | `@OneToMany(cascade=ALL, fetch=EAGER)` | Visit history, ordered by date |

**Key Methods**:
| Method | Description |
|--------|-------------|
| `LocalDate getBirthDate()` | Returns pet's birth date |
| `void setBirthDate(LocalDate birthDate)` | Sets pet's birth date |
| `PetType getType()` | Returns pet type |
| `void setType(PetType type)` | Sets pet type |
| `Collection<Visit> getVisits()` | Returns all visits |
| `void addVisit(Visit visit)` | Adds a new visit to the history |

**JPA Annotations**:
- `@Entity` - Marks as JPA entity
- `@Table(name = "pets")` - Maps to pets table
- `@ManyToOne` - Reference to PetType
- `@JoinColumn(name = "type_id")` - Foreign key to types table
- `@OneToMany(cascade = CascadeType.ALL, fetch = FetchType.EAGER)` - Manages visits
- `@OrderBy("date ASC")` - Visits sorted chronologically

**Collection Type**:
- Uses `LinkedHashSet` for visits to maintain insertion order and prevent duplicates

**Date Formatting**:
- Uses Spring's `@DateTimeFormat` for automatic parsing from HTML forms

---

### 3. PetType (Entity)

**Purpose**: Represents a category/species of pet (e.g., cat, dog, hamster, bird).

**Type**: `@Entity` mapped to `types` table

**Inheritance**: Extends `NamedEntity` (inherits name, id)

**Key Fields**:
- Inherits `name` from NamedEntity (the type name like "cat", "dog")
- Inherits `id` from BaseEntity

**JPA Annotations**:
- `@Entity` - Marks as JPA entity
- `@Table(name = "types")` - Maps to types table

**Usage**:
- Serves as a reference data entity
- Used in dropdown selections for pet registration
- Provides type classification for pets

**Simplicity Rationale**:
- Intentionally minimal as it's a simple lookup/reference table
- Business logic exists in PetTypeFormatter and PetTypeRepository

---

### 4. Visit (Entity)

**Purpose**: Represents a veterinary visit for a specific pet.

**Type**: `@Entity` mapped to `visits` table

**Inheritance**: Extends `BaseEntity` (inherits id)

**Key Fields**:
| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| `date` | `LocalDate` | `@DateTimeFormat("yyyy-MM-dd")` | Visit date (defaults to today) |
| `description` | `String` | `@NotBlank` | Reason for visit / visit notes |

**Key Methods**:
| Method | Description |
|--------|-------------|
| `Visit()` | Constructor - initializes date to current date |
| `LocalDate getDate()` | Returns visit date |
| `void setDate(LocalDate date)` | Sets visit date |
| `String getDescription()` | Returns visit description |
| `void setDescription(String description)` | Sets visit description |

**JPA Annotations**:
- `@Entity` - Marks as JPA entity
- `@Table(name = "visits")` - Maps to visits table
- `@Column(name = "visit_date")` - Maps date field to visit_date column

**Default Behavior**:
- Constructor automatically sets date to `LocalDate.now()`
- Ensures every visit has a valid date even if not explicitly set

**Validation**:
- Description is required (`@NotBlank`)
- Additional date validation performed in VisitController (cannot be in future)

---

### 5. OwnerRepository (Repository Interface)

**Purpose**: Data access interface for Owner entities using Spring Data JPA.

**Type**: Spring Data JPA Repository

**Inheritance**: Extends `JpaRepository<Owner, Integer>`

**Query Methods**:
| Method | Description | Query Type |
|--------|-------------|------------|
| `Page<Owner> findByLastNameStartingWith(String lastName, Pageable pageable)` | Finds owners by last name prefix with pagination | Derived query |
| `Optional<Owner> findById(Integer id)` | Finds owner by ID, returns Optional | Inherited (overridden for documentation) |

**Pagination Support**:
- Uses Spring Data's `Pageable` interface
- Returns `Page<Owner>` with metadata (total pages, total elements, etc.)
- Enables efficient large dataset handling

**Query Derivation**:
- `findByLastNameStartingWith` - Spring Data auto-generates SQL:
  ```sql
  SELECT * FROM owners WHERE last_name LIKE :lastName%
  ```

**Usage Pattern**:
```java
// Paginated search
Pageable pageable = PageRequest.of(0, 5); // page 0, size 5
Page<Owner> results = repository.findByLastNameStartingWith("Smith", pageable);

// Find by ID
Optional<Owner> owner = repository.findById(1);
owner.ifPresent(o -> System.out.println(o.getFirstName()));
```

**Inherited Methods** (from JpaRepository):
- `save(Owner)` - Create or update
- `delete(Owner)` - Delete owner
- `findAll()` - Retrieve all owners
- And many more...

---

### 6. PetTypeRepository (Repository Interface)

**Purpose**: Data access interface for PetType entities.

**Type**: Spring Data JPA Repository

**Inheritance**: Extends `JpaRepository<PetType, Integer>`

**Custom Query Methods**:
| Method | Description | Query Type |
|--------|-------------|------------|
| `List<PetType> findPetTypes()` | Retrieves all pet types sorted by name | `@Query` JPQL |

**JPQL Query**:
```java
@Query("SELECT ptype FROM PetType ptype ORDER BY ptype.name")
List<PetType> findPetTypes();
```

**Usage**:
- Primarily used to populate dropdown lists in forms
- Returns all types in alphabetical order
- Used by PetTypeFormatter for String-to-PetType conversion

**Design Note**:
- Could use `findAll(Sort.by("name"))` but explicit query provides clarity
- Returns `List` instead of `Page` as complete dataset is always needed

---

### 7. OwnerController (Web Controller)

**Purpose**: Handles HTTP requests for owner CRUD operations and search functionality.

**Type**: `@Controller` - Spring MVC controller

**Base URL Patterns**:
- `/owners/new` - Create new owner
- `/owners/find` - Search form
- `/owners` - Search results / list all
- `/owners/{ownerId}` - View owner details
- `/owners/{ownerId}/edit` - Edit owner

**Dependencies**:
| Dependency | Type | Injection Method |
|------------|------|------------------|
| `owners` | `OwnerRepository` | Constructor injection |

**Key Request Mappings**:

#### Create Owner
| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/owners/new` | Displays create form |
| `POST` | `/owners/new` | Processes form submission |

**POST Logic**:
- Validates owner data using Bean Validation
- Saves to database via repository
- Redirects to owner details page
- Adds flash message: "New Owner Created"

#### Search Owners
| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/owners/find` | Displays search form |
| `GET` | `/owners?page=1` | Processes search with pagination |

**Search Logic**:
1. Empty lastName → searches all owners
2. No results → shows error message
3. Exactly 1 result → redirects to owner details
4. Multiple results → shows paginated list

**Pagination**:
- Page size: 5 owners per page
- Uses `PageRequest.of(page-1, 5)` (0-based indexing)
- Adds pagination metadata to model (currentPage, totalPages, totalItems)

#### View Owner
| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/owners/{ownerId}` | Displays owner details with pets and visits |

#### Update Owner
| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/owners/{ownerId}/edit` | Displays edit form |
| `POST` | `/owners/{ownerId}/edit` | Processes update |

**Update Logic**:
- Validates owner data
- Checks ID in form matches URL parameter
- Saves updates
- Redirects with flash message: "Owner Values Updated"

**Security Features**:
- `@InitBinder` disallows binding to `id` field (prevents ID tampering)
- ID mismatch validation on updates
- Throws `IllegalArgumentException` for non-existent IDs

**Model Attributes**:
- `@ModelAttribute("owner")` - Auto-loads owner for all methods with `{ownerId}`
- Converts 404 scenarios to meaningful exceptions

**Error Handling**:
- Uses `RedirectAttributes` for flash messages
- Validation errors keep user on form with error messages
- Search errors shown inline with rejected field values

---

### 8. PetController (Web Controller)

**Purpose**: Manages pet registration and editing for owners.

**Type**: `@Controller` - Spring MVC controller

**Base URL Patterns**: `/owners/{ownerId}/pets/*`

**Request Mapping Class-Level**:
```java
@RequestMapping("/owners/{ownerId}")
```
All pet operations are scoped under an owner.

**Dependencies**:
| Dependency | Type | Injection Method |
|------------|------|------------------|
| `owners` | `OwnerRepository` | Constructor injection |
| `types` | `PetTypeRepository` | Constructor injection |

**Key Request Mappings**:

#### Create Pet
| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/owners/{ownerId}/pets/new` | Displays pet creation form |
| `POST` | `/owners/{ownerId}/pets/new` | Processes new pet |

**Creation Logic**:
- Validates pet using `PetValidator`
- Checks for duplicate names within owner's pets
- Validates birth date not in future
- Adds pet to owner and saves (cascade)
- Flash message: "New Pet has been Added"

#### Edit Pet
| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/owners/{ownerId}/pets/{petId}/edit` | Displays pet edit form |
| `POST` | `/owners/{ownerId}/pets/{petId}/edit` | Processes pet update |

**Update Logic**:
- Validates pet using `PetValidator`
- Checks for duplicate names (excluding current pet)
- Validates birth date not in future
- Updates existing pet properties (name, birthDate, type)
- Saves owner (cascade updates pet)
- Flash message: "Pet details has been edited"

**Model Attributes**:

| Attribute | Method | Scope | Description |
|-----------|--------|-------|-------------|
| `types` | `populatePetTypes()` | All requests | Loads all pet types for dropdown |
| `owner` | `findOwner(@PathVariable ownerId)` | All requests | Loads owner from URL |
| `pet` | `findPet(@PathVariable petId)` | Requests with {petId} | Loads pet or creates new |

**Validation Strategy**:
- **Custom Validator**: Uses `PetValidator` (registered via `@InitBinder`)
- **Controller Validation**: Additional business rules (duplicate names, future dates)
- **Bean Validation**: Inherited from NamedEntity (`@NotBlank` on name)

**Business Rules Enforced**:
1. Pet name must be unique per owner
2. Birth date cannot be in the future
3. Pet type is required for new pets
4. Name and birth date are required fields

**Security Features**:
- `@InitBinder` disallows binding to owner `id` field
- Pet validator initialized for `pet` binding

**Helper Method**:
```java
private void updatePetDetails(Owner owner, Pet pet)
```
- Updates existing pet properties if found
- Adds new pet if not found in owner's collection
- Ensures data consistency

---

### 9. VisitController (Web Controller)

**Purpose**: Manages scheduling and recording of veterinary visits for pets.

**Type**: `@Controller` - Spring MVC controller

**Base URL Patterns**: `/owners/{ownerId}/pets/{petId}/visits/*`

**Dependencies**:
| Dependency | Type | Injection Method |
|------------|------|------------------|
| `owners` | `OwnerRepository` | Constructor injection |

**Key Request Mappings**:

#### Create Visit
| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/owners/{ownerId}/pets/{petId}/visits/new` | Displays visit form |
| `POST` | `/owners/{ownerId}/pets/{petId}/visits/new` | Processes new visit |

**Visit Creation Flow**:
1. `loadPetWithVisit()` called before controller method (via `@ModelAttribute`)
2. Loads owner from repository
3. Finds pet within owner's pets
4. Creates new Visit with current date
5. Temporarily adds visit to pet (for form display)
6. On POST: validates description, saves owner (cascade saves visit)

**Model Attributes**:

| Attribute | Method | Scope | Description |
|-----------|--------|-------|-------------|
| `visit` | `loadPetWithVisit(...)` | All requests | Creates visit and loads context |
| Additional | Added to Map | All requests | `pet` and `owner` added to model |

**loadPetWithVisit Method**:
```java
@ModelAttribute("visit")
public Visit loadPetWithVisit(@PathVariable("ownerId") int ownerId, 
                              @PathVariable("petId") int petId,
                              Map<String, Object> model)
```

**Responsibilities**:
1. Fetches owner by ID (throws exception if not found)
2. Fetches pet from owner (throws exception if not found)
3. Adds `pet` and `owner` to model
4. Creates new Visit instance
5. Pre-adds visit to pet's visit collection

**Processing Logic**:
- Validates visit description (`@NotBlank`)
- Uses `owner.addVisit(petId, visit)` for consistency
- Saves via owner repository (cascade saves visit)
- Flash message: "Your visit has been booked"
- Redirects to owner details page

**Security Features**:
- `@InitBinder` disallows binding to `id` field
- Validates owner exists before pet lookup
- Validates pet belongs to specified owner

**Error Handling**:
- Throws `IllegalArgumentException` if owner not found
- Throws `IllegalArgumentException` if pet not found for owner
- Validation errors return to form with error messages

**Design Pattern**:
- **Pre-population**: Visit added to pet before form display
- **Cascade Save**: Visit saved via owner save operation
- **Fresh Data**: Always loads fresh owner/pet data (no session caching)

---

### 10. PetValidator (Validator)

**Purpose**: Implements custom validation rules for Pet entities.

**Type**: Spring `Validator` implementation

**Interface**: Implements `org.springframework.validation.Validator`

**Validation Rules**:

| Field | Validation | Error Code | Condition |
|-------|------------|------------|-----------|
| `name` | Required | "required" | Name is blank or null |
| `type` | Required | "required" | Type is null AND pet is new |
| `birthDate` | Required | "required" | Birth date is null |

**Key Methods**:

#### validate(Object obj, Errors errors)
```java
public void validate(Object obj, Errors errors)
```
**Logic**:
1. Casts object to Pet
2. Validates name using `StringUtils.hasText()`
3. Validates type only for new pets (`pet.isNew()`)
4. Validates birthDate is not null

**Rationale**:
- Type validation only for new pets (editing might have different rules)
- Uses Spring's `StringUtils.hasText()` for robust null/empty checking
- Rejects values with consistent error code "required"

#### supports(Class<?> clazz)
```java
public boolean supports(Class<?> clazz)
```
**Returns**: `true` if class is assignable from Pet

**Usage in Controller**:
```java
@InitBinder("pet")
public void initPetBinder(WebDataBinder dataBinder) {
    dataBinder.setValidator(new PetValidator());
}
```

**Why Custom Validator?**:
> "We're not using Bean Validation annotations here because it is easier to define such validation rule in Java."

**Advantages**:
- Conditional validation (type only for new pets)
- Centralized validation logic
- Easier to test independently
- More flexibility than declarative annotations

**Complementary Validation**:
- Works alongside Bean Validation annotations
- Controllers add additional business rules (duplicate names, future dates)

---

### 11. PetTypeFormatter (Formatter)

**Purpose**: Converts between PetType objects and String representations for Spring MVC form binding.

**Type**: Spring `Formatter<PetType>` implementation

**Interface**: Implements `org.springframework.format.Formatter<PetType>`

**Component**: Registered as `@Component` for auto-discovery

**Dependencies**:
| Dependency | Type | Injection Method |
|------------|------|------------------|
| `types` | `PetTypeRepository` | Constructor injection |

**Key Methods**:

#### print(PetType petType, Locale locale)
```java
public String print(PetType petType, Locale locale)
```
**Purpose**: Converts PetType to String for display

**Logic**:
- Returns `petType.getName()` if not null
- Returns `"<null>"` if name is null

**Use Cases**:
- Rendering selected value in dropdowns
- Displaying pet type in read-only views
- Form pre-population for edit scenarios

#### parse(String text, Locale locale)
```java
public PetType parse(String text, Locale locale) throws ParseException
```
**Purpose**: Converts String to PetType for form submission

**Logic**:
1. Fetches all pet types from repository
2. Iterates to find matching name
3. Returns matching PetType
4. Throws `ParseException` if not found

**Error Handling**:
```java
throw new ParseException("type not found: " + text, 0);
```

**Use Cases**:
- Processing form submissions
- Converting dropdown selections to entities
- Binding request parameters to PetType fields

**Spring MVC Integration**:
- Automatically registered by `@Component`
- Spring MVC uses it for `PetType` fields in forms
- Enables seamless HTML select → PetType binding

**Example Form Binding**:
```html
<select name="type">
  <option value="cat">cat</option>
  <option value="dog">dog</option>
</select>
```
When submitted, Spring MVC:
1. Calls `parse("cat", locale)`
2. Returns corresponding PetType entity
3. Binds to `pet.type` field

**Performance Consideration**:
- Loads all types on each parse (acceptable for small reference tables)
- Could be optimized with caching if types table grows large

**Design Pattern**:
- Replaces legacy `PropertyEditor` approach (pre-Spring 3.0)
- Thread-safe (unlike PropertyEditors)
- More modern and maintainable

---

## Usage Examples

### Example 1: Creating a New Owner with Pets

```java
// In OwnerController
@PostMapping("/owners/new")
public String processCreationForm(@Valid Owner owner, BindingResult result,
                                  RedirectAttributes redirectAttributes) {
    if (result.hasErrors()) {
        redirectAttributes.addFlashAttribute("error", 
            "There was an error in creating the owner.");
        return VIEWS_OWNER_CREATE_OR_UPDATE_FORM;
    }
    
    this.owners.save(owner);  // Saves owner and cascades to pets
    redirectAttributes.addFlashAttribute("message", "New Owner Created");
    return "redirect:/owners/" + owner.getId();
}
```

**Flow**:
1. User submits form with owner data
2. Spring MVC binds form to Owner object
3. `@Valid` triggers Bean Validation
4. If errors, returns to form with flash message
5. Repository saves owner
6. Redirect to owner details page with success message

---

### Example 2: Searching Owners with Pagination

```java
// In OwnerController
@GetMapping("/owners")
public String processFindForm(@RequestParam(defaultValue = "1") int page,
                              Owner owner, BindingResult result, Model model) {
    String lastName = owner.getLastName();
    if (lastName == null) {
        lastName = "";  // Search all
    }
    
    Page<Owner> ownersResults = findPaginatedForOwnersLastName(page, lastName);
    
    if (ownersResults.isEmpty()) {
        result.rejectValue("lastName", "notFound", "not found");
        return "owners/findOwners";
    }
    
    if (ownersResults.getTotalElements() == 1) {
        owner = ownersResults.iterator().next();
        return "redirect:/owners/" + owner.getId();
    }
    
    return addPaginationModel(page, model, ownersResults);
}

private Page<Owner> findPaginatedForOwnersLastName(int page, String lastname) {
    Pageable pageable = PageRequest.of(page - 1, 5);  // 5 per page, 0-based index
    return owners.findByLastNameStartingWith(lastname, pageable);
}
```

**Search Scenarios**:
- **Empty search**: Returns all owners (paginated)
- **No matches**: Shows error on search form
- **Single match**: Redirects directly to owner details
- **Multiple matches**: Shows paginated list

---

### Example 3: Adding a Pet to an Owner

```java
// In PetController
@PostMapping("/owners/{ownerId}/pets/new")
public String processCreationForm(Owner owner, @Valid Pet pet, 
                                  BindingResult result,
                                  RedirectAttributes redirectAttributes) {
    
    // Check for duplicate name
    if (StringUtils.hasText(pet.getName()) && pet.isNew() 
        && owner.getPet(pet.getName(), true) != null) {
        result.rejectValue("name", "duplicate", "already exists");
    }
    
    // Validate birth date
    LocalDate currentDate = LocalDate.now();
    if (pet.getBirthDate() != null && pet.getBirthDate().isAfter(currentDate)) {
        result.rejectValue("birthDate", "typeMismatch.birthDate");
    }
    
    if (result.hasErrors()) {
        return VIEWS_PETS_CREATE_OR_UPDATE_FORM;
    }
    
    owner.addPet(pet);
    this.owners.save(owner);  // Cascade saves pet
    redirectAttributes.addFlashAttribute("message", "New Pet has been Added");
    return "redirect:/owners/{ownerId}";
}
```

**Validation Steps**:
1. PetValidator checks required fields
2. Controller checks duplicate names
3. Controller validates birth date not in future
4. If valid, adds pet to owner
5. Saves owner (cascade creates pet record)

---

### Example 4: Scheduling a Visit

```java
// In VisitController
@ModelAttribute("visit")
public Visit loadPetWithVisit(@PathVariable("ownerId") int ownerId,
                              @PathVariable("petId") int petId,
                              Map<String, Object> model) {
    // Load owner
    Optional<Owner> optionalOwner = owners.findById(ownerId);
    Owner owner = optionalOwner.orElseThrow(() -> 
        new IllegalArgumentException("Owner not found with id: " + ownerId));
    
    // Load pet from owner
    Pet pet = owner.getPet(petId);
    if (pet == null) {
        throw new IllegalArgumentException(
            "Pet with id " + petId + " not found for owner with id " + ownerId);
    }
    
    // Add to model
    model.put("pet", pet);
    model.put("owner", owner);
    
    // Create and add visit
    Visit visit = new Visit();  // Defaults to current date
    pet.addVisit(visit);
    return visit;
}

@PostMapping("/owners/{ownerId}/pets/{petId}/visits/new")
public String processNewVisitForm(@ModelAttribute Owner owner,
                                  @PathVariable int petId,
                                  @Valid Visit visit,
                                  BindingResult result,
                                  RedirectAttributes redirectAttributes) {
    if (result.hasErrors()) {
        return "pets/createOrUpdateVisitForm";
    }
    
    owner.addVisit(petId, visit);  // Adds visit with validation
    this.owners.save(owner);  // Cascade saves visit
    redirectAttributes.addFlashAttribute("message", "Your visit has been booked");
    return "redirect:/owners/{ownerId}";
}
```

**Flow**:
1. GET request triggers `loadPetWithVisit()` → creates Visit with current date
2. Form displayed with pre-populated date
3. User enters description
4. POST validates description required
5. `owner.addVisit()` validates pet exists
6. Save cascades to visit table

---

### Example 5: Repository Query Patterns

```java
// Finding owners by last name (paginated)
Pageable pageable = PageRequest.of(0, 10);  // Page 1, 10 items
Page<Owner> owners = ownerRepository.findByLastNameStartingWith("Sm", pageable);

// Accessing page metadata
int totalPages = owners.getTotalPages();
long totalElements = owners.getTotalElements();
boolean hasNext = owners.hasNext();

// Getting current page content
List<Owner> currentPageOwners = owners.getContent();

// Finding owner by ID
Optional<Owner> owner = ownerRepository.findById(123);
owner.ifPresent(o -> {
    System.out.println(o.getFirstName() + " " + o.getLastName());
    List<Pet> pets = o.getPets();  // Eager loaded
    pets.forEach(pet -> System.out.println("  - " + pet.getName()));
});

// Finding all pet types (ordered)
List<PetType> types = petTypeRepository.findPetTypes();
types.forEach(type -> System.out.println(type.getName()));
```

---

### Example 6: Working with Entity Relationships

```java
// Create owner with pet and visit in one transaction
Owner owner = new Owner();
owner.setFirstName("John");
owner.setLastName("Doe");
owner.setAddress("123 Main St");
owner.setCity("Springfield");
owner.setTelephone("1234567890");

Pet pet = new Pet();
pet.setName("Fluffy");
pet.setBirthDate(LocalDate.of(2020, 5, 15));
pet.setType(petTypeRepository.findPetTypes().get(0));  // First type

Visit visit = new Visit();  // Date defaults to today
visit.setDescription("Regular checkup");

pet.addVisit(visit);
owner.addPet(pet);

ownerRepository.save(owner);  // Cascade saves pet and visit

// Later, retrieve with all relationships loaded (eager fetch)
Owner retrieved = ownerRepository.findById(owner.getId()).get();
retrieved.getPets().forEach(p -> {
    System.out.println("Pet: " + p.getName());
    p.getVisits().forEach(v -> 
        System.out.println("  Visit on " + v.getDate() + ": " + v.getDescription())
    );
});
```

---

## Validation Patterns

### 1. Bean Validation (Declarative)

**Used in Entities**:

```java
// Owner entity
@NotBlank
private String address;

@Pattern(regexp = "\\d{10}", message = "{telephone.invalid}")
private String telephone;

// Visit entity
@NotBlank
private String description;

// NamedEntity (inherited by Pet, PetType)
@NotBlank
private String name;
```

**Triggered by**: `@Valid` annotation in controller methods

---

### 2. Custom Validator (Programmatic)

**PetValidator**:
```java
@Override
public void validate(Object obj, Errors errors) {
    Pet pet = (Pet) obj;
    
    if (!StringUtils.hasText(pet.getName())) {
        errors.rejectValue("name", REQUIRED, REQUIRED);
    }
    
    if (pet.isNew() && pet.getType() == null) {
        errors.rejectValue("type", REQUIRED, REQUIRED);
    }
    
    if (pet.getBirthDate() == null) {
        errors.rejectValue("birthDate", REQUIRED, REQUIRED);
    }
}
```

**Registered in Controller**:
```java
@InitBinder("pet")
public void initPetBinder(WebDataBinder dataBinder) {
    dataBinder.setValidator(new PetValidator());
}
```

---

### 3. Controller-Level Business Validation

**Duplicate Name Check**:
```java
if (StringUtils.hasText(pet.getName()) && pet.isNew() 
    && owner.getPet(pet.getName(), true) != null) {
    result.rejectValue("name", "duplicate", "already exists");
}
```

**Future Date Validation**:
```java
LocalDate currentDate = LocalDate.now();
if (pet.getBirthDate() != null && pet.getBirthDate().isAfter(currentDate)) {
    result.rejectValue("birthDate", "typeMismatch.birthDate");
}
```

**ID Mismatch Validation**:
```java
if (!Objects.equals(owner.getId(), ownerId)) {
    result.rejectValue("id", "mismatch", 
        "The owner ID in the form does not match the URL.");
}
```

---

### 4. Entity-Level Validation

**Owner.addVisit()**:
```java
public void addVisit(Integer petId, Visit visit) {
    Assert.notNull(petId, "Pet identifier must not be null!");
    Assert.notNull(visit, "Visit must not be null!");
    
    Pet pet = getPet(petId);
    Assert.notNull(pet, "Invalid Pet identifier!");
    
    pet.addVisit(visit);
}
```

Uses Spring's `Assert` utility for precondition checking.

---

## Architectural Notes

### 1. Cascade Operations Strategy

**Owner → Pet Cascade**:
```java
@OneToMany(cascade = CascadeType.ALL, fetch = FetchType.EAGER)
```
- ALL operations (persist, merge, remove, refresh, detach) cascade to pets
- Saves owner → automatically saves all pets
- Deletes owner → automatically deletes all pets

**Pet → Visit Cascade**:
```java
@OneToMany(cascade = CascadeType.ALL, fetch = FetchType.EAGER)
```
- ALL operations cascade to visits
- Deleting pet → deletes all associated visits

**Pet → PetType** (No Cascade):
```java
@ManyToOne
@JoinColumn(name = "type_id")
```
- PetType is reference data, should not cascade
- Deleting pet does NOT delete pet type

---

### 2. Eager vs Lazy Fetch Strategy

**Eager Fetch Used**:
```java
@OneToMany(fetch = FetchType.EAGER)
```

**Rationale**:
- Owner details page displays pets AND visits in single view
- Avoids lazy initialization exceptions
- Simplifies controller logic (no explicit fetch needed)
- Acceptable for small collections (owners typically have few pets)

**Trade-off**:
- Always loads full object graph
- Could cause performance issues with many pets/visits
- For production at scale, consider lazy fetch with JOIN FETCH queries

---

### 3. Controller Design Patterns

**Constructor Injection**:
```java
public OwnerController(OwnerRepository owners) {
    this.owners = owners;
}
```
- Immutable dependencies
- Easier testing (can pass mocks)
- Required dependencies clear in constructor

**@ModelAttribute Pre-loading**:
```java
@ModelAttribute("owner")
public Owner findOwner(@PathVariable(required = false) Integer ownerId) {
    return ownerId == null ? new Owner() 
        : owners.findById(ownerId).orElseThrow(...);
}
```
- Loads owner once per request
- Available to all methods automatically
- Reduces code duplication

**Flash Attributes for Messages**:
```java
redirectAttributes.addFlashAttribute("message", "New Owner Created");
```
- Survives redirect
- Displayed on target page
- Automatically cleared after display

---

### 4. Security Best Practices

**Disallow ID Binding**:
```java
@InitBinder
public void setAllowedFields(WebDataBinder dataBinder) {
    dataBinder.setDisallowedFields("id");
}
```
- Prevents ID tampering via form manipulation
- Users cannot change entity IDs through forms

**ID Mismatch Validation**:
```java
if (!Objects.equals(owner.getId(), ownerId)) {
    // Reject
}
```
- Ensures URL ID matches form data
- Prevents cross-entity updates

**Existence Validation**:
```java
Owner owner = owners.findById(ownerId)
    .orElseThrow(() -> new IllegalArgumentException(...));
```
- Always validates entities exist
- Provides clear error messages
- Fails fast for invalid IDs

---

### 5. Query Optimization Opportunities

**Current Approach** (works for small datasets):
- Eager fetch loads all relationships
- Paginated search loads 5 owners at a time

**For Production at Scale**:
- Use `@EntityGraph` for selective eager loading
- Implement DTO projections for list views
- Use JOIN FETCH in custom queries
- Consider caching for reference data (PetType)

**Example Optimization**:
```java
@Query("SELECT o FROM Owner o LEFT JOIN FETCH o.pets WHERE o.id = :id")
Optional<Owner> findByIdWithPets(@Param("id") Integer id);
```

---

### 6. Validation Layer Architecture

**Three-Layer Validation**:

1. **Bean Validation** (Entity level)
   - Data type constraints
   - Required fields
   - Format patterns (telephone, dates)

2. **Custom Validators** (Domain level)
   - Complex field rules
   - Conditional validation
   - Cross-field validation

3. **Controller Validation** (Business level)
   - Duplicate checks
   - Referential integrity
   - Business rule enforcement

**Benefits**:
- Separation of concerns
- Reusable validation logic
- Clear error messages
- Fail-fast approach

---

## Best Practices Demonstrated

### 1. Domain-Driven Design
- Rich domain models with behavior (Owner.addPet, Pet.addVisit)
- Entity relationships reflect real-world concepts
- Business logic in entities, not just getters/setters

### 2. Repository Pattern
- Clean data access abstraction
- Technology-agnostic interface
- Spring Data eliminates boilerplate

### 3. MVC Separation
- Controllers handle HTTP concerns
- Entities handle domain logic
- Repositories handle persistence

### 4. Validation Strategy
- Multi-layered validation
- Declarative where possible
- Programmatic for complex rules

### 5. Error Handling
- Meaningful exception messages
- User-friendly error displays
- Flash messages for feedback

### 6. RESTful URL Design
- Resource-oriented URLs
- Hierarchical structure (owner → pet → visit)
- Standard HTTP methods (GET, POST)

### 7. Form Handling
- POST-Redirect-GET pattern
- Flash attributes for messages
- Binding validation
- Security controls (disallowed fields)

---

## Common Pitfalls & Solutions

### Pitfall 1: Lazy Initialization Exceptions
**Problem**: Accessing pets/visits after session closed
**Solution**: Use EAGER fetch or JOIN FETCH queries

### Pitfall 2: Duplicate Pet Names
**Problem**: Multiple pets with same name
**Solution**: Controller validates uniqueness per owner

### Pitfall 3: Cascade Delete Accidents
**Problem**: Deleting owner deletes all pets/visits
**Solution**: Intentional design; could add soft delete if needed

### Pitfall 4: N+1 Query Problem
**Problem**: Loading owners list triggers queries per owner
**Solution**: EAGER fetch mitigates; consider JOIN FETCH for optimization

### Pitfall 5: Date Validation
**Problem**: Birth dates in future
**Solution**: Controller-level validation checks date <= today

---

## Testing Considerations

### Unit Testing Controllers
```java
@WebMvcTest(OwnerController.class)
class OwnerControllerTests {
    @MockBean
    private OwnerRepository owners;
    
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void testProcessFindFormSuccess() throws Exception {
        // Mock repository
        // Perform request
        // Verify response
    }
}
```

### Integration Testing Repositories
```java
@DataJpaTest
class OwnerRepositoryTests {
    @Autowired
    private OwnerRepository owners;
    
    @Test
    void testFindByLastNameStartingWith() {
        // Test pagination and search
    }
}
```

### Testing Validators
```java
class PetValidatorTests {
    private PetValidator validator = new PetValidator();
    
    @Test
    void testValidatePetWithoutName() {
        Pet pet = new Pet();
        Errors errors = new BeanPropertyBindingResult(pet, "pet");
        validator.validate(pet, errors);
        assertTrue(errors.hasFieldErrors("name"));
    }
}
```

---

## Extension Points

### Adding New Features
1. **Soft Delete**: Add `deleted` flag to Owner/Pet
2. **Audit Trail**: Extend BaseEntity with created/modified dates
3. **Pet Photos**: Add `photoUrl` to Pet entity
4. **Email Notifications**: Service layer for visit reminders
5. **Search Enhancement**: Full-text search, advanced filters
6. **Authorization**: Add Spring Security for role-based access

### Integration Opportunities
- **REST API**: Add `@RestController` for JSON endpoints
- **Events**: Publish domain events (OwnerCreated, VisitScheduled)
- **Caching**: Add `@Cacheable` for reference data
- **Async Processing**: Email notifications via `@Async`

---

## Performance Considerations

### Current Performance Characteristics
- **Eager Fetch**: Fast for small datasets, potential N+1 issues at scale
- **Pagination**: Efficient for large owner lists
- **No Caching**: Simple but could benefit from cache

### Recommended Optimizations
1. **Cache PetTypes**: Rarely change, frequently accessed
2. **Lazy Fetch + DTO**: For list views, load minimal data
3. **Query Optimization**: Use JOIN FETCH for detail views
4. **Database Indexing**: Index on last_name for search performance
5. **Connection Pooling**: Configure HikariCP for production

---

## Summary

The `owner` package is a well-architected, feature-complete module demonstrating Spring Boot best practices:

- **Comprehensive CRUD**: Full lifecycle management for owners, pets, and visits
- **Rich Domain Model**: Entities with behavior, not anemic data structures
- **Clean Architecture**: Clear separation of concerns across layers
- **Robust Validation**: Multi-layered validation strategy
- **User-Friendly**: Pagination, search, flash messages, error handling
- **Security-Conscious**: ID protection, existence validation, input sanitization
- **Maintainable**: Constructor injection, immutable collections, clear naming

This package serves as an excellent reference implementation for Spring MVC applications with JPA persistence.
