# Package: org.springframework.samples.petclinic.model

## Overview

The `org.springframework.samples.petclinic.model` package provides the foundational domain model layer for the Spring PetClinic application. This package contains JPA mapped superclasses that establish a reusable entity inheritance hierarchy, centralizing common entity properties and behaviors. These base classes are designed using the **Template Method** and **Inheritance** patterns to promote code reuse and maintain consistency across all domain entities in the application.

## Purpose

- **Domain Model Foundation**: Provides reusable JPA entity superclasses that form the base layer of the domain model
- **Common Attributes**: Centralizes common entity properties (id, name, firstName, lastName) to eliminate duplication
- **Entity Lifecycle Management**: Implements standardized persistence mechanisms and entity state detection
- **Validation**: Incorporates Bean Validation annotations to ensure data integrity at the model layer
- **Serialization Support**: Implements `Serializable` interface to support session storage and distributed scenarios

## Architecture

This package represents the **lowest layer** in the domain model architecture:

```
Application Layer (Controllers)
        ↓
Domain Layer (Entities: Owner, Pet, Vet, etc.)
        ↓
Model Base Layer (BaseEntity, NamedEntity, Person) ← THIS PACKAGE
        ↓
JPA/Hibernate (Persistence Layer)
```

**Design Characteristics:**
- All classes are annotated with `@MappedSuperclass` (not `@Entity`)
- Classes are not persisted as standalone entities
- Attributes and mappings are inherited by concrete entity subclasses
- No dependencies on other application packages (pure foundation layer)

## Classes

### BaseEntity

**Purpose**: Base superclass for all JPA entities in the application, providing identity management and persistence state detection.

**Type**: `@MappedSuperclass`, `implements Serializable`

**Key Fields**:
| Field | Type | Annotations | Description |
|-------|------|-------------|-------------|
| `id` | `Integer` | `@Id`, `@GeneratedValue(strategy = IDENTITY)` | Primary key with auto-increment strategy |

**Key Methods**:
| Method | Return Type | Description |
|--------|-------------|-------------|
| `getId()` | `Integer` | Returns the entity's primary key identifier |
| `setId(Integer id)` | `void` | Sets the entity's primary key identifier |
| `isNew()` | `boolean` | Determines if entity is transient (not yet persisted). Returns `true` if `id` is `null` |

**JPA Mapping Details**:
- Uses `GenerationType.IDENTITY` for primary key generation
- Delegates ID generation to the database (auto-increment)
- Compatible with MySQL, PostgreSQL, and H2 databases

**Relationships**:
- Extended by: `NamedEntity`, `Person`
- Implements: `java.io.Serializable`

**Usage Example**:
```java
@Entity
@Table(name = "custom_entities")
public class CustomEntity extends BaseEntity {
    @Column(name = "description")
    private String description;
    
    // Inherits: id, getId(), setId(), isNew()
}

// Usage
CustomEntity entity = new CustomEntity();
entity.isNew(); // returns true (id is null)
repository.save(entity);
entity.isNew(); // returns false (id has been assigned)
```

**Architectural Notes**:
- The `isNew()` method is critical for JPA repositories to distinguish between insert and update operations
- `Serializable` implementation enables entities to be stored in HTTP sessions
- Using `Integer` (nullable) instead of `int` allows detection of new entities via `null` check

---

### NamedEntity

**Purpose**: Abstract superclass for entities that have a single `name` property, extending `BaseEntity` with naming capabilities and validation.

**Type**: `@MappedSuperclass`, `extends BaseEntity`

**Key Fields**:
| Field | Type | Annotations | Description |
|-------|------|-------------|-------------|
| `name` | `String` | `@Column`, `@NotBlank` | Required name property with validation |

**Key Methods**:
| Method | Return Type | Description |
|--------|-------------|-------------|
| `getName()` | `String` | Returns the entity's name |
| `setName(String name)` | `void` | Sets the entity's name |
| `toString()` | `String` | Returns name or `"<null>"` if name is null |

**Validation**:
- `@NotBlank`: Ensures name is not null, not empty, and contains at least one non-whitespace character
- Validation triggers during entity persistence and can be used for form validation

**Relationships**:
- Extends: `BaseEntity`
- Extended by: `Pet`, `PetType`, `Specialty` (in owner and vet packages)

**Usage Example**:
```java
@Entity
@Table(name = "types")
public class PetType extends NamedEntity {
    // Inherits: id, name, getId(), setId(), getName(), setName(), isNew()
}

// Usage
PetType petType = new PetType();
petType.setName("Dog");
System.out.println(petType); // Output: "Dog"

PetType emptyType = new PetType();
System.out.println(emptyType); // Output: "<null>"
```

**Inherited Hierarchy**:
```
NamedEntity
  ├── id (from BaseEntity)
  ├── name (own property)
  └── Methods: getId(), setId(), isNew(), getName(), setName(), toString()
```

**Architectural Notes**:
- Designed for lookup/reference entities that require only a name (e.g., PetType, Specialty)
- The `toString()` override provides safe string representation for debugging and logging
- Bean Validation integrates with Spring's validation framework for automatic form validation

---

### Person

**Purpose**: Abstract superclass representing a person with first and last name properties, used for human-related entities.

**Type**: `@MappedSuperclass`, `extends BaseEntity`

**Key Fields**:
| Field | Type | Annotations | Description |
|-------|------|-------------|-------------|
| `firstName` | `String` | `@Column`, `@NotBlank` | Required first name with validation |
| `lastName` | `String` | `@Column`, `@NotBlank` | Required last name with validation |

**Key Methods**:
| Method | Return Type | Description |
|--------|-------------|-------------|
| `getFirstName()` | `String` | Returns the person's first name |
| `setFirstName(String firstName)` | `void` | Sets the person's first name |
| `getLastName()` | `String` | Returns the person's last name |
| `setLastName(String lastName)` | `void` | Sets the person's last name |

**Validation**:
- Both `firstName` and `lastName` are validated with `@NotBlank`
- Ensures person entities always have valid name data
- Validation occurs during form submission and entity persistence

**Relationships**:
- Extends: `BaseEntity`
- Extended by: `Owner`, `Vet` (in owner and vet packages)

**Usage Example**:
```java
@Entity
@Table(name = "owners")
public class Owner extends Person {
    @Column(name = "address")
    private String address;
    
    @Column(name = "city")
    private String city;
    
    // Inherits: id, firstName, lastName and all methods
}

// Usage
Owner owner = new Owner();
owner.setFirstName("John");
owner.setLastName("Doe");
owner.setAddress("123 Main St");
owner.setCity("Springfield");
```

**Inherited Hierarchy**:
```
Person
  ├── id (from BaseEntity)
  ├── firstName (own property)
  ├── lastName (own property)
  └── Methods: getId(), setId(), isNew(), getFirstName(), setFirstName(), 
               getLastName(), setLastName()
```

**Architectural Notes**:
- Separates person-specific attributes from general named entities
- Establishes a clear semantic distinction between "things with names" and "people with names"
- Enables consistent handling of person data across different entity types (owners, vets)

---

## Inheritance Hierarchy

```
                    java.io.Serializable
                            ↑
                            │
                      BaseEntity (@MappedSuperclass)
                      - id: Integer
                      - getId(), setId(), isNew()
                            ↑
                ┌───────────┴───────────┐
                │                       │
          NamedEntity              Person
      (@MappedSuperclass)      (@MappedSuperclass)
        - name: String          - firstName: String
        - getName()             - lastName: String
        - setName()             - getFirstName(), setFirstName()
        - toString()            - getLastName(), setLastName()
                │                       │
        ┌───────┴────────┐             ├──────────┐
        │                │             │          │
     PetType        Specialty       Owner       Vet
    (@Entity)      (@Entity)      (@Entity)  (@Entity)
    
    
                BaseEntity
                    ↑
                    │
                  Pet (@Entity)
              - name: String
            (implements NamedEntity pattern without extending it)
```

## Validation Patterns

### Bean Validation Integration

The model classes leverage Jakarta Bean Validation (formerly JSR-303/JSR-380) for declarative validation:

**Validation Annotations Used**:
- `@NotBlank`: Validates that a string is not null, not empty (""), and contains at least one non-whitespace character

**Validation Trigger Points**:
1. **Form Submission**: Spring MVC automatically validates `@Valid` annotated command objects
2. **JPA Persistence**: Hibernate validates entities before insert/update operations
3. **Programmatic**: Manual validation via `Validator` interface

**Example Validation Flow**:
```java
// In Controller
@PostMapping("/owners/new")
public String processCreationForm(@Valid Owner owner, BindingResult result) {
    if (result.hasErrors()) {
        // Validation failed - firstName or lastName was blank
        return "owners/createOrUpdateOwnerForm";
    }
    // Validation passed
    this.owners.save(owner);
    return "redirect:/owners/" + owner.getId();
}
```

**Validation Error Messages**:
- Default messages defined in `src/main/resources/messages/messages.properties`
- Can be customized per field using `@NotBlank(message = "...")`

## JPA Mapping Details

### @MappedSuperclass Annotation

**Purpose**: Indicates that a class provides persistent entity state and mapping information to be inherited by subclasses, but is not itself an entity.

**Key Characteristics**:
- Classes annotated with `@MappedSuperclass` are **not** queryable entities
- Cannot be the target of entity relationships
- Mappings (columns, IDs, etc.) are inherited by concrete `@Entity` subclasses
- Each concrete entity gets its own table with inherited columns

**Example Mapping**:

```java
// BaseEntity (not an entity, just provides id mapping)
@MappedSuperclass
public class BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
}

// Owner (concrete entity with its own table)
@Entity
@Table(name = "owners")
public class Owner extends Person {
    // Table: owners
    // Columns: id (inherited), first_name (inherited), last_name (inherited), 
    //          address, city, telephone
}
```

**Resulting Database Schema**:
```sql
-- No table for BaseEntity or Person (they are @MappedSuperclass)

-- Table for Owner entity
CREATE TABLE owners (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,  -- from BaseEntity
    first_name VARCHAR(255) NOT NULL,        -- from Person
    last_name VARCHAR(255) NOT NULL,         -- from Person
    address VARCHAR(255),                     -- from Owner
    city VARCHAR(255),                        -- from Owner
    telephone VARCHAR(20)                     -- from Owner
);

-- Table for Vet entity
CREATE TABLE vets (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,  -- from BaseEntity
    first_name VARCHAR(255) NOT NULL,        -- from Person
    last_name VARCHAR(255) NOT NULL          -- from Person
);

-- Table for PetType entity
CREATE TABLE types (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,  -- from BaseEntity
    name VARCHAR(80) NOT NULL                -- from NamedEntity
);
```

### Primary Key Strategy

**Strategy**: `GenerationType.IDENTITY`

**How It Works**:
- Database auto-generates primary key values using auto-increment mechanism
- JPA retrieves generated ID immediately after insert
- Compatible with MySQL (`AUTO_INCREMENT`), PostgreSQL (`SERIAL`), H2 (`IDENTITY`)

**Advantages**:
- Simple and widely supported
- No need for sequence tables or hi/lo algorithms
- Immediate ID availability after persistence

**Considerations**:
- Requires database round-trip to get generated ID
- Batch inserts are less efficient (each insert needs immediate ID retrieval)
- Cannot generate IDs for transient entities (ID assigned only after `persist()`)

## Dependencies

### Downstream Dependencies (Packages Using This Package)

| Package | Classes Using Model | Relationship |
|---------|-------------------|--------------|
| `org.springframework.samples.petclinic.owner` | `Owner` extends `Person`<br/>`Pet` extends `NamedEntity`<br/>`PetType` extends `NamedEntity` | Core domain entities |
| `org.springframework.samples.petclinic.vet` | `Vet` extends `Person`<br/>`Specialty` extends `NamedEntity` | Core domain entities |

### Upstream Dependencies (External Libraries)

| Dependency | Purpose |
|------------|---------|
| `jakarta.persistence.*` | JPA annotations for ORM mapping |
| `jakarta.validation.constraints.*` | Bean Validation annotations |
| `java.io.Serializable` | Enable serialization for session storage |

**No Internal Application Dependencies**: This package has zero dependencies on other application packages, making it the true foundation layer.

## Design Patterns

### 1. Template Method Pattern

The inheritance hierarchy uses the Template Method pattern where base classes define the structure (id, name, person fields) and subclasses fill in specific details.

```java
// Template structure in BaseEntity
public class BaseEntity {
    protected Integer id;  // Template: all entities have an ID
    
    public boolean isNew() {  // Template algorithm
        return this.id == null;
    }
}

// Concrete implementation
@Entity
public class Owner extends Person {
    // Fills in the template with specific owner data
}
```

### 2. Single Responsibility Principle (SRP)

Each class has a single, well-defined responsibility:
- **BaseEntity**: Identity and persistence state management
- **NamedEntity**: Single-name entity support
- **Person**: Person-specific (first/last name) entity support

### 3. Open/Closed Principle

The classes are:
- **Open for extension**: Designed to be extended by concrete entities
- **Closed for modification**: Core functionality is stable and shouldn't require changes

### 4. DRY (Don't Repeat Yourself)

Common entity attributes and behaviors are defined once in base classes and reused across all entities.

## Best Practices

### When to Extend Each Class

**Extend `BaseEntity` when**:
- Entity requires only an ID
- Entity doesn't fit the "named" or "person" patterns
- Example: Visit (has ID but no inherent name)

**Extend `NamedEntity` when**:
- Entity represents a thing/concept with a single name
- Entity is often used for lookup/reference data
- Examples: PetType ("Dog", "Cat"), Specialty ("Dentistry")

**Extend `Person` when**:
- Entity represents a human with first and last names
- Examples: Owner, Vet, Employee

### Validation Best Practices

1. **Use `@NotBlank` for required strings**: More appropriate than `@NotNull` or `@NotEmpty` for text fields
2. **Add custom validations in subclasses**: Use `@Pattern`, `@Size`, etc., for specific requirements
3. **Group related validations**: Consider validation groups for complex scenarios (create vs. update)

### Example: Adding Custom Validation

```java
@Entity
@Table(name = "owners")
public class Owner extends Person {
    
    @Column(name = "telephone")
    @NotBlank
    @Pattern(regexp = "^[0-9]{10}$", message = "Phone must be 10 digits")
    private String telephone;
    
    // Inherits @NotBlank validation for firstName and lastName from Person
}
```

## Testing Considerations

### Testing Entity State

```java
@Test
void testIsNewEntity() {
    Owner owner = new Owner();
    assertTrue(owner.isNew()); // No ID assigned yet
    
    owner.setId(1);
    assertFalse(owner.isNew()); // ID assigned
}
```

### Testing Validation

```java
@Test
void testNameValidation() {
    PetType petType = new PetType();
    petType.setName("");  // Blank name
    
    ValidatorFactory factory = Validation.buildDefaultValidatorFactory();
    Validator validator = factory.getValidator();
    Set<ConstraintViolation<PetType>> violations = validator.validate(petType);
    
    assertEquals(1, violations.size());
    assertEquals("must not be blank", violations.iterator().next().getMessage());
}
```

### Testing Inheritance

```java
@Test
void testPersonInheritance() {
    Owner owner = new Owner();
    owner.setFirstName("John");
    owner.setLastName("Doe");
    
    // Verify Person methods work
    assertEquals("John", owner.getFirstName());
    assertEquals("Doe", owner.getLastName());
    
    // Verify BaseEntity methods work
    assertTrue(owner.isNew());
}
```

## Common Pitfalls

### ❌ Don't: Make mapped superclasses into entities

```java
// WRONG: BaseEntity should never be @Entity
@Entity
@MappedSuperclass  // Conflicting annotations
public class BaseEntity { ... }
```

### ❌ Don't: Query mapped superclasses directly

```java
// WRONG: Cannot query @MappedSuperclass
entityManager.createQuery("SELECT b FROM BaseEntity b", BaseEntity.class);
```

### ❌ Don't: Create relationships to mapped superclasses

```java
// WRONG: Cannot reference @MappedSuperclass in relationships
@ManyToOne
private BaseEntity entity;  // Will fail
```

### ✅ Do: Extend for concrete entities

```java
// CORRECT: Extend mapped superclass in concrete @Entity
@Entity
@Table(name = "custom_entities")
public class CustomEntity extends BaseEntity {
    // Inherits id and all BaseEntity behavior
}
```

### ✅ Do: Use isNew() for persistence logic

```java
// CORRECT: Use isNew() to determine entity state
if (entity.isNew()) {
    // Handle new entity
} else {
    // Handle existing entity
}
```

## Summary

The `org.springframework.samples.petclinic.model` package provides a robust, reusable foundation for the PetClinic domain model. By centralizing common entity attributes and behaviors in well-designed mapped superclasses, it:

- **Eliminates code duplication** across entity classes
- **Enforces consistency** in entity structure and validation
- **Simplifies entity development** through inheritance
- **Maintains clean architecture** with zero application dependencies
- **Supports testability** with clear contracts and behaviors

This package exemplifies **domain-driven design principles** and **object-oriented best practices**, serving as an excellent reference for building layered JPA applications with Spring Boot.
