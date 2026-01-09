# Package: org.springframework.samples.petclinic.system

## Overview

The `system` package provides the core infrastructure and cross-cutting concerns for the PetClinic application. It configures caching with JCache, internationalization (i18n) support, and basic web navigation. This package is independent of domain business logic and provides foundational services that all other packages depend on. It follows Spring Boot configuration best practices with clear separation between caching, web MVC configuration, and controller logic.

## Architecture & Design Patterns

### Design Patterns Used
- **Configuration Pattern**: Spring `@Configuration` classes for infrastructure setup
- **Interceptor Pattern**: `LocaleChangeInterceptor` for cross-cutting language switching
- **Cache-Aside Pattern**: JCache configuration with statistics monitoring
- **Session State Pattern**: Session-scoped locale storage
- **MVC (Model-View-Controller)**: Controllers for welcome and error demonstration

### Package Dependencies
- **Internal Dependencies**:
  - None - This package is independent of other application packages
- **External Dependencies**:
  - Spring Framework (Core, MVC, Cache, Boot)
  - JCache API (`javax.cache`)
  - Spring Web MVC (Locale resolvers, interceptors)

### Architectural Role
This is the **infrastructure/system configuration package** that provides:
1. **Cross-Cutting Concerns**: Caching, internationalization
2. **Application Entry Points**: Home page, error demonstration
3. **Framework Configuration**: Web MVC customization, cache setup
4. **No Business Logic**: Intentionally separate from domain packages (owner, vet, etc.)

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│          org.springframework.samples.petclinic.system   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Configuration Layer                                    │
│  ┌────────────────────┐   ┌──────────────────────┐    │
│  │ CacheConfiguration │   │ WebConfiguration     │    │
│  │  - JCache setup    │   │  - i18n support      │    │
│  │  - Vets cache      │   │  - Locale resolver   │    │
│  │  - Statistics      │   │  - Interceptor       │    │
│  └────────────────────┘   └──────────────────────┘    │
│                                                         │
│  Controller Layer                                       │
│  ┌──────────────────┐   ┌────────────────────────┐    │
│  │ WelcomeController│   │ CrashController        │    │
│  │  - Home page     │   │  - Error demonstration │    │
│  └──────────────────┘   └────────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Used by all packages  │
              │  - owner               │
              │  - vet                 │
              │  - visit               │
              └────────────────────────┘
```

---

## Classes

### 1. CacheConfiguration (Configuration)

**Purpose**: Configures JCache API caching for the application with monitoring enabled via JMX statistics.

**Type**: `@Configuration` class with cache setup

**Annotations**:
- `@Configuration(proxyBeanMethods = false)` - Configuration class without proxy overhead
- `@EnableCaching` - Enables Spring's annotation-driven cache management

**Key Methods**:
| Method | Return Type | Description |
|--------|-------------|-------------|
| `petclinicCacheConfigurationCustomizer()` | `JCacheManagerCustomizer` | Creates the "vets" cache with custom configuration |
| `cacheConfiguration()` | `Configuration<Object, Object>` | Provides JCache configuration with statistics enabled |

**Cache Configuration Details**:

#### petclinicCacheConfigurationCustomizer()
```java
@Bean
public JCacheManagerCustomizer petclinicCacheConfigurationCustomizer() {
    return cm -> cm.createCache("vets", cacheConfiguration());
}
```

**Purpose**: 
- Creates a cache named **"vets"** for veterinarian data
- Applies custom cache configuration
- Executed during application startup

**Why "vets" cache?**
- Veterinarian data changes infrequently
- Loaded frequently for display purposes
- Ideal candidate for caching to reduce database queries

#### cacheConfiguration()
```java
private javax.cache.configuration.Configuration<Object, Object> cacheConfiguration() {
    return new MutableConfiguration<>().setStatisticsEnabled(true);
}
```

**Configuration Options**:
- **Statistics Enabled**: `true` - Enables JMX monitoring
- **JCache Standard**: Uses `MutableConfiguration` from JCache API
- **Extensibility**: Size limits and eviction policies configured via JCache implementation (e.g., Caffeine)

**JCache Implementation Note**:
> The JCache API standard provides limited configuration options. Implementation-specific settings (cache size, eviction policy, TTL) must be configured through the chosen JCache provider (typically Caffeine in Spring Boot).

**JMX Monitoring**:
When statistics are enabled, the following metrics become available:
- Cache hit rate
- Cache miss rate
- Number of cache entries
- Eviction count
- Average get time

**Usage in Application**:
```java
// In VetRepository or VetController
@Cacheable("vets")
public Collection<Vet> findAll() {
    // Database query only executed on cache miss
}
```

**Spring Boot Auto-Configuration**:
- Spring Boot detects JCache on classpath
- Auto-configures cache manager (typically Caffeine)
- This configuration customizes the default setup

**Performance Impact**:
- **Without Cache**: Database query on every veterinarian list request
- **With Cache**: Database query only on first request or cache expiration
- **Statistics**: Minimal overhead, valuable for monitoring

---

### 2. WebConfiguration (Configuration)

**Purpose**: Configures internationalization (i18n) support, enabling users to switch languages dynamically via URL parameters.

**Type**: `@Configuration` class implementing `WebMvcConfigurer`

**Annotations**:
- `@Configuration` - Marks as Spring configuration class
- `@SuppressWarnings("unused")` - Suppresses IDE warnings for beans used by Spring

**Author**: Anuj Ashok Potdar

**Interface Implementation**: `WebMvcConfigurer` - Provides callback methods for customizing Spring MVC configuration

**Key Components**:

| Component | Type | Description |
|-----------|------|-------------|
| `localeResolver()` | `LocaleResolver` | Manages user's language preference in session |
| `localeChangeInterceptor()` | `LocaleChangeInterceptor` | Intercepts requests to detect language change |
| `addInterceptors()` | Override method | Registers the locale change interceptor |

---

#### localeResolver()
```java
@Bean
public LocaleResolver localeResolver() {
    SessionLocaleResolver resolver = new SessionLocaleResolver();
    resolver.setDefaultLocale(Locale.ENGLISH);
    return resolver;
}
```

**Purpose**: Determines and stores the user's current locale (language setting)

**Implementation**: `SessionLocaleResolver`
- **Storage**: User's locale stored in HTTP session
- **Persistence**: Locale persists across requests during the session
- **Default**: English (`Locale.ENGLISH`) for new sessions
- **Scope**: Per-user, per-session

**Alternative Implementations**:
- `CookieLocaleResolver` - Stores locale in browser cookie
- `AcceptHeaderLocaleResolver` - Uses HTTP Accept-Language header
- `FixedLocaleResolver` - Single locale for all users

**Why SessionLocaleResolver?**
- User-specific language preference
- No cookie dependencies
- Simple session-based state management
- Resets on session expiration

**Supported Locales** (defined in message bundles):
- English (default)
- Spanish
- German (mentioned in examples)

---

#### localeChangeInterceptor()
```java
@Bean
public LocaleChangeInterceptor localeChangeInterceptor() {
    LocaleChangeInterceptor interceptor = new LocaleChangeInterceptor();
    interceptor.setParamName("lang");
    return interceptor;
}
```

**Purpose**: Detects language change requests via URL parameter

**Configuration**:
- **Parameter Name**: `lang`
- **Trigger**: Any request with `?lang=XX` parameter
- **Action**: Updates the locale in the `LocaleResolver`

**Usage Examples**:
```
http://localhost:8080/owners?lang=es    → Switch to Spanish
http://localhost:8080/owners?lang=de    → Switch to German
http://localhost:8080/owners?lang=en    → Switch to English
http://localhost:8080/owners/1?lang=es  → Spanish on owner detail page
```

**How It Works**:
1. User clicks language link with `?lang=es`
2. `LocaleChangeInterceptor.preHandle()` executes before controller
3. Interceptor reads `lang` parameter
4. Calls `LocaleResolver.setLocale(locale, request, response)`
5. Locale stored in session
6. Controller renders with new locale
7. Subsequent requests use stored locale (no `?lang=` needed)

**Interceptor Execution Order**:
```
Request → LocaleChangeInterceptor → Controller → View
```

---

#### addInterceptors()
```java
@Override
public void addInterceptors(InterceptorRegistry registry) {
    registry.addInterceptor(localeChangeInterceptor());
}
```

**Purpose**: Registers the locale change interceptor with Spring MVC

**Scope**: Applied to all requests (no path patterns specified)

**Execution**: Runs before every controller method

**WebMvcConfigurer Pattern**:
- Provides non-invasive MVC customization
- No XML configuration required
- Type-safe Java configuration
- Multiple configurers can coexist

---

### Internationalization Implementation

**Message Bundle Structure**:
```
src/main/resources/messages/
├── messages.properties          # Default (English)
├── messages_es.properties       # Spanish
├── messages_de.properties       # German
└── messages_XX.properties       # Other languages
```

**Example Message Properties**:
```properties
# messages.properties (English)
welcome=Welcome to PetClinic

# messages_es.properties (Spanish)
welcome=Bienvenido a PetClinic

# messages_de.properties (German)
welcome=Willkommen bei PetClinic
```

**Thymeleaf Template Usage**:
```html
<!-- Uses current locale from LocaleResolver -->
<h2 th:text="#{welcome}">Welcome</h2>

<!-- Language switcher -->
<a th:href="@{/(lang=es)}">Español</a>
<a th:href="@{/(lang=en)}">English</a>
<a th:href="@{/(lang=de)}">Deutsch</a>
```

**Spring Boot Auto-Configuration**:
Spring Boot automatically:
1. Creates `MessageSource` bean
2. Loads `messages*.properties` files
3. Uses `LocaleResolver` for locale detection
4. Integrates with Thymeleaf for `#{...}` expressions

---

### 3. WelcomeController (Controller)

**Purpose**: Handles requests to the application home page (root URL).

**Type**: `@Controller` - Spring MVC controller

**Annotations**:
- `@Controller` - Marks as MVC controller component

**Visibility**: Package-private (no public modifier) - Only accessible within `system` package

**Request Mappings**:

| Method | URL | HTTP Method | View | Description |
|--------|-----|-------------|------|-------------|
| `welcome()` | `/` | GET | `welcome` | Application home page |

**Implementation**:
```java
@GetMapping("/")
public String welcome() {
    return "welcome";
}
```

**Method Details**:

#### welcome()
**Purpose**: Renders the application landing page

**Flow**:
1. User navigates to `http://localhost:8080/`
2. Spring MVC routes to `WelcomeController.welcome()`
3. Returns view name `"welcome"`
4. Thymeleaf resolves to `templates/welcome.html`
5. Renders home page with navigation menu

**View Template**: `src/main/resources/templates/welcome.html`

**Typical Content**:
- Application logo/branding
- Welcome message (internationalized)
- Navigation links to main features:
  - Find owners
  - View veterinarians
  - Error demonstration
- Background image or hero section

**No Model Data**: 
- Returns only view name
- No data binding required for home page
- Static content with i18n support

**Simplicity Rationale**:
- Home page is purely navigational
- No business logic required
- No database queries
- Minimal controller code follows single responsibility principle

**Testing Considerations**:
```java
@WebMvcTest(WelcomeController.class)
class WelcomeControllerTests {
    @Test
    void testWelcome() throws Exception {
        mockMvc.perform(get("/"))
            .andExpect(status().isOk())
            .andExpect(view().name("welcome"));
    }
}
```

---

### 4. CrashController (Controller)

**Purpose**: Demonstrates exception handling and error page rendering by intentionally throwing a runtime exception.

**Type**: `@Controller` - Spring MVC controller for testing/demonstration

**Annotations**:
- `@Controller` - Marks as MVC controller component

**Author**: Michael Isvy

**Visibility**: Package-private (no public modifier)

**Request Mappings**:

| Method | URL | HTTP Method | Behavior | Description |
|--------|-----|-------------|----------|-------------|
| `triggerException()` | `/oups` | GET | Throws `RuntimeException` | Demonstrates error handling |

**Implementation**:
```java
@GetMapping("/oups")
public String triggerException() {
    throw new RuntimeException(
        "Expected: controller used to showcase what " + 
        "happens when an exception is thrown");
}
```

**Method Details**:

#### triggerException()
**Purpose**: Intentionally throws an exception to demonstrate error handling flow

**Exception Message**:
```
Expected: controller used to showcase what happens when an exception is thrown
```

**Exception Type**: `RuntimeException` (unchecked exception)

**Error Handling Flow**:
1. User navigates to `http://localhost:8080/oups`
2. Controller method executes
3. `RuntimeException` thrown
4. Spring MVC exception handling activates
5. Custom error view `error.html` rendered
6. User sees friendly error page with exception details

**Error View**: `src/main/resources/templates/error.html`

**Why "oups"?**
- Playful URL mimicking French "oops"
- Memorable for developers testing error handling
- Non-production endpoint (not linked from main navigation)

**Spring Boot Error Handling**:

Spring Boot provides automatic error handling:
- **Default Behavior**: `/error` endpoint with `BasicErrorController`
- **Custom Error Page**: `templates/error.html` overrides default
- **Error Attributes**: Exception message, stack trace, timestamp
- **HTTP Status**: 500 Internal Server Error

**Error Template Variables** (available in `error.html`):
```html
<h2 th:text="${status}">500</h2>
<p th:text="${error}">Internal Server Error</p>
<p th:text="${message}">Exception message</p>
<p th:text="${timestamp}">Timestamp</p>
<!-- Stack trace (development only) -->
<pre th:text="${trace}">Stack trace</pre>
```

**Use Cases**:
1. **Development**: Test error page styling and content
2. **Demo**: Show stakeholders error handling
3. **Testing**: Verify exception logging and monitoring
4. **Training**: Teach developers about Spring error handling

**Production Considerations**:
- **Remove or Restrict**: Consider removing in production or restricting to admin users
- **Monitoring Integration**: Exceptions should be logged and monitored (e.g., Sentry, New Relic)
- **User-Friendly Messages**: Error page should not expose stack traces to end users

**Security Note**:
```java
// In application.properties for production:
server.error.include-stacktrace=never
server.error.include-message=always
server.error.include-binding-errors=never
server.error.include-exception=false
```

**Alternative: Custom Exception Handler**:
For more control, use `@ControllerAdvice`:
```java
@ControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(RuntimeException.class)
    public String handleRuntimeException(RuntimeException ex, Model model) {
        model.addAttribute("message", ex.getMessage());
        return "error";
    }
}
```

**Testing**:
```java
@WebMvcTest(CrashController.class)
class CrashControllerTests {
    @Test
    void testTriggerException() throws Exception {
        mockMvc.perform(get("/oups"))
            .andExpect(status().is5xxServerError())
            .andExpect(view().name("error"));
    }
}
```

---

## Configuration Details

### Caching Configuration

**JCache Provider**: Spring Boot auto-configures Caffeine as the JCache implementation

**Cache Name**: `vets`

**Configuration Options**:

| Setting | Value | Description |
|---------|-------|-------------|
| Statistics | Enabled | JMX monitoring available |
| Size Limit | Provider default | Configured in JCache implementation |
| Eviction Policy | Provider default | Typically LRU (Least Recently Used) |
| TTL (Time-to-Live) | Provider default | Cache entries never expire by default |

**Customizing Cache Size** (via `application.properties`):
```properties
# Caffeine cache spec (Spring Boot 2.x+)
spring.cache.cache-names=vets
spring.cache.caffeine.spec=maximumSize=500,expireAfterWrite=10m
```

**Cache Statistics Access** (JMX):
- **JMX Bean**: `javax.cache:type=CacheStatistics,CacheManager=*,Cache=vets`
- **Metrics**: Hit rate, miss rate, size, evictions
- **Monitoring Tools**: JConsole, VisualVM, Spring Boot Actuator

**Cache Usage Example**:
```java
// In VetController or service layer
@Cacheable("vets")
public Collection<Vet> findAll() {
    // Expensive database query
    return vetRepository.findAll();
}

// Cache eviction (when data changes)
@CacheEvict(value = "vets", allEntries = true)
public void updateVet(Vet vet) {
    vetRepository.save(vet);
}
```

**Cache Warming** (Optional):
```java
@Component
public class CacheWarmer implements ApplicationListener<ContextRefreshedEvent> {
    @Autowired
    private VetService vetService;
    
    @Override
    public void onApplicationEvent(ContextRefreshedEvent event) {
        vetService.findAll();  // Populate cache on startup
    }
}
```

---

### Internationalization Configuration

**Locale Storage**: HTTP Session via `SessionLocaleResolver`

**Language Change Parameter**: `lang` (e.g., `?lang=es`)

**Default Locale**: English (`Locale.ENGLISH`)

**Message Bundle Location**: `src/main/resources/messages/messages*.properties`

**Supported Languages** (based on available message bundles):
- English (en) - Default
- Spanish (es)
- German (de)
- Extensible - Add new `messages_XX.properties` files

**Message Resolution Order**:
1. User's session locale (if set)
2. Browser's `Accept-Language` header (if no session locale)
3. Default locale (English)

**Locale Switching Flow**:
```
User clicks "Español" link (?lang=es)
         ↓
LocaleChangeInterceptor detects parameter
         ↓
Updates SessionLocaleResolver
         ↓
Locale stored in HTTP session
         ↓
Thymeleaf uses new locale for rendering
         ↓
All subsequent requests use Spanish until changed
```

**Message Key Examples**:
```properties
# messages.properties
welcome=Welcome
owner.lastName=Last Name
pet.name=Name
vet.specialties=Specialties

# messages_es.properties
welcome=Bienvenido
owner.lastName=Apellido
pet.name=Nombre
vet.specialties=Especialidades
```

**Thymeleaf Integration**:
```html
<!-- Message expression -->
<label th:text="#{owner.lastName}">Last Name</label>

<!-- With parameters -->
<p th:text="#{welcome.message(${owner.firstName})}">Welcome, John</p>

<!-- messages.properties -->
<!-- welcome.message=Welcome, {0}! -->
```

**Date/Number Formatting** (Locale-aware):
```html
<!-- Date formatting -->
<td th:text="${{pet.birthDate}}">2020-01-15</td>

<!-- Number formatting -->
<td th:text="${{price}}">$1,234.56</td>
```

**Programmatic Locale Access**:
```java
@Controller
public class ExampleController {
    @GetMapping("/example")
    public String example(Locale locale, Model model) {
        // Current locale available as method parameter
        model.addAttribute("currentLocale", locale.getDisplayName());
        return "example";
    }
}
```

---

## Usage Examples

### Example 1: Using the Welcome Page

**User Access**:
```
Navigate to: http://localhost:8080/
```

**Expected Behavior**:
1. `WelcomeController.welcome()` handles request
2. Returns `"welcome"` view name
3. Thymeleaf renders `templates/welcome.html`
4. Page displays in user's current locale (default: English)
5. Navigation menu provides links to main features

**Welcome Template Structure**:
```html
<!DOCTYPE html>
<html xmlns:th="https://www.thymeleaf.org">
<head>
    <title th:text="#{welcome}">Welcome</title>
</head>
<body>
    <h1 th:text="#{welcome}">Welcome to PetClinic</h1>
    <img th:src="@{/resources/images/pets.png}" alt="PetClinic"/>
    <nav>
        <a th:href="@{/owners/find}" th:text="#{findOwners}">Find Owners</a>
        <a th:href="@{/vets.html}" th:text="#{veterinarians}">Veterinarians</a>
    </nav>
</body>
</html>
```

---

### Example 2: Switching Languages

**Spanish Language Switch**:
```
1. User on: http://localhost:8080/owners
2. Clicks "Español" link: http://localhost:8080/owners?lang=es
3. Page reloads in Spanish
4. Session stores locale=es
5. All subsequent pages render in Spanish
```

**Implementation in Template**:
```html
<!-- Language switcher in layout header -->
<nav class="language-switcher">
    <a th:href="@{''(lang=en)}">🇬🇧 English</a>
    <a th:href="@{''(lang=es)}">🇪🇸 Español</a>
    <a th:href="@{''(lang=de)}">🇩🇪 Deutsch</a>
</nav>
```

**Thymeleaf URL Syntax**:
- `@{''(lang=es)}` → Adds `?lang=es` to current URL
- `@{/(lang=es)}` → Adds `?lang=es` to root URL
- `@{/owners(lang=es)}` → Creates `/owners?lang=es`

**Server-Side Flow**:
```java
// Automatic - no controller code needed
LocaleChangeInterceptor.preHandle()
    → Reads "lang" parameter
    → LocaleResolver.setLocale(new Locale("es"))
    → Locale stored in session
    → Continue to controller
```

**Persistent Across Requests**:
```
Request 1: /owners?lang=es  → Locale set to Spanish
Request 2: /owners/1        → Still Spanish (from session)
Request 3: /vets.html       → Still Spanish (from session)
Request 4: /?lang=en        → Switches back to English
```

---

### Example 3: Testing Error Handling

**Trigger Error**:
```
Navigate to: http://localhost:8080/oups
```

**Execution Flow**:
```
1. Browser sends GET /oups
2. CrashController.triggerException() executes
3. RuntimeException thrown with message
4. Spring MVC catches exception
5. Routes to /error endpoint
6. Error attributes populated (status, message, timestamp)
7. templates/error.html rendered
8. User sees friendly error page
```

**Error Page Display**:
```html
<!-- error.html -->
<h1>Something happened...</h1>
<p th:text="${message}">Expected: controller used to showcase...</p>
<p th:text="${timestamp}">2025-01-09 12:34:56</p>
<!-- Stack trace only in dev profile -->
<pre th:if="${trace}" th:text="${trace}">...</pre>
```

**HTTP Response**:
```
HTTP/1.1 500 Internal Server Error
Content-Type: text/html
```

**Logging Output** (typical):
```
ERROR o.s.web.servlet.mvc.method.annotation.ExceptionHandlerExceptionResolver - 
Resolved [java.lang.RuntimeException: Expected: controller used to showcase 
what happens when an exception is thrown]
```

---

### Example 4: Cache Performance Monitoring

**Accessing Cache Statistics via JMX**:

1. **Enable JMX** (enabled by default in Spring Boot)
2. **Connect with JConsole**: `jconsole` or VisualVM
3. **Navigate to MBean**: `javax.cache:type=CacheStatistics,CacheManager=*,Cache=vets`
4. **View Metrics**:
   - CacheHits: Number of successful cache lookups
   - CacheMisses: Number of cache misses (database queries)
   - CacheHitPercentage: Hit rate
   - CachePuts: Number of entries added

**Programmatic Statistics Access**:
```java
@Autowired
private CacheManager cacheManager;

public void printCacheStats() {
    Cache vetsCache = cacheManager.getCache("vets");
    if (vetsCache instanceof JCache) {
        JCache jCache = (JCache) vetsCache;
        MBeanServer mBeanServer = ManagementFactory.getPlatformMBeanServer();
        ObjectName objectName = new ObjectName(
            "javax.cache:type=CacheStatistics,CacheManager=*,Cache=vets");
        // Query statistics
    }
}
```

**Spring Boot Actuator Integration** (optional):
```properties
# application.properties
management.endpoints.web.exposure.include=caches
```

**Access Endpoint**:
```
GET http://localhost:8080/actuator/caches
```

**Response**:
```json
{
  "cacheManagers": {
    "cacheManager": {
      "caches": {
        "vets": {
          "target": "org.springframework.cache.jcache.JCacheCache"
        }
      }
    }
  }
}
```

---

### Example 5: Custom Message Bundles

**Adding a New Language** (French):

1. **Create Message Bundle**:
```properties
# src/main/resources/messages/messages_fr.properties
welcome=Bienvenue
owner.lastName=Nom de famille
pet.name=Nom
vet.specialties=Spécialités
findOwners=Trouver des propriétaires
```

2. **Add Language Switcher Link**:
```html
<a th:href="@{''(lang=fr)}">🇫🇷 Français</a>
```

3. **Restart Application** (no code changes needed)

4. **Test**:
```
http://localhost:8080/?lang=fr
→ Page displays in French
```

**Message with Parameters**:
```properties
# messages.properties
owner.pets.count=This owner has {0} pet(s)

# messages_fr.properties
owner.pets.count=Ce propriétaire a {0} animal(aux)
```

**Template Usage**:
```html
<p th:text="#{owner.pets.count(${owner.pets.size()})}">
    This owner has 3 pet(s)
</p>
```

---

## Architectural Notes

### 1. Independence from Business Logic

**Design Principle**: The `system` package provides infrastructure **orthogonal** to business domains.

**Key Characteristics**:
- No dependencies on `owner`, `vet`, or `visit` packages
- Other packages depend on `system`, not vice versa
- Can be reused across different Spring Boot applications
- Changes to business logic don't affect system configuration

**Dependency Graph**:
```
system (infrastructure)
  ↑ uses
  ├── owner
  ├── vet
  └── visit
```

**Benefits**:
- **Testability**: Can test system components independently
- **Reusability**: Configuration can be extracted to shared library
- **Maintainability**: Changes isolated to appropriate layer
- **Clarity**: Clear separation of concerns

---

### 2. Configuration Best Practices

**Package-Private Controllers**:
```java
@Controller
class WelcomeController {  // No public modifier
    // Implementation
}
```

**Rationale**:
- Controllers are Spring-managed beans (visibility doesn't matter)
- Reduces public API surface
- Prevents accidental external usage
- Follows principle of least privilege

**@Configuration(proxyBeanMethods = false)**:
```java
@Configuration(proxyBeanMethods = false)
class CacheConfiguration {
    // Configuration
}
```

**Performance Optimization**:
- Disables CGLIB proxying of `@Configuration` class
- Reduces startup time
- Appropriate when `@Bean` methods don't call each other
- Recommended by Spring Boot for modern applications

**Constructor Injection** (not used here but recommended):
```java
// If controllers had dependencies
@Controller
class ExampleController {
    private final ExampleService service;
    
    public ExampleController(ExampleService service) {
        this.service = service;
    }
}
```

---

### 3. Cache Strategy

**Cache-Aside Pattern**:
```
1. Application requests data
2. Check cache first
3. If cache hit → return cached data
4. If cache miss → query database, populate cache, return data
```

**Why "vets" Cache?**
- **Read-Heavy**: Veterinarian list frequently viewed
- **Infrequent Updates**: Vet data rarely changes
- **Expensive Query**: May include JOIN with specialties
- **High ROI**: Significant performance gain for minimal complexity

**Cache Key Generation**:
```java
@Cacheable("vets")  // Default key: method parameters (none = single entry)
public Collection<Vet> findAll() {
    return vetRepository.findAll();
}
```

**Cache Eviction Strategy**:
```java
@CacheEvict(value = "vets", allEntries = true)
public void updateVet(Vet vet) {
    // Update database
    // Cache cleared, will repopulate on next read
}
```

**Monitoring Importance**:
- Statistics enabled to track cache effectiveness
- Identify if cache is being utilized
- Tune size/eviction policies based on metrics
- Detect cache thrashing or excessive misses

---

### 4. Internationalization Best Practices

**Session vs. Cookie Storage**:

| Approach | Pros | Cons |
|----------|------|------|
| **Session** (current) | Simple, server-controlled, no cookie issues | Lost on session expiration |
| **Cookie** | Persists across sessions | Cookie size limit, privacy concerns |
| **Accept-Language** | Automatic browser detection | User can't override easily |

**Current Choice**: Session is appropriate because:
- PetClinic is session-based (owner management)
- Language preference is temporary (per-session)
- Simplifies implementation

**Message Bundle Organization**:
```
messages/
├── messages.properties              # Base (English)
├── messages_es.properties           # Spanish translations
├── messages_de.properties           # German translations
└── messages_validation.properties   # Validation messages (optional)
```

**Best Practices**:
1. **Consistent Keys**: Use hierarchical naming (`owner.lastName`, `pet.birthDate`)
2. **Fallback**: Always provide base `messages.properties` (English)
3. **Validation Messages**: Can override Bean Validation messages
4. **Parameter Placeholders**: Use `{0}`, `{1}` for dynamic content

**Locale-Aware Formatting**:
```java
// Spring automatically uses locale for date/number formatting
@DateTimeFormat(pattern = "yyyy-MM-dd")
private LocalDate birthDate;

// In template
<td th:text="${{pet.birthDate}}">2020-01-15</td>
<!-- Formats according to locale: US=01/15/2020, DE=15.01.2020 -->
```

---

### 5. Error Handling Strategy

**Spring Boot Error Handling Layers**:

1. **Controller-Level** (`@ExceptionHandler`):
   ```java
   @ExceptionHandler(ResourceNotFoundException.class)
   public String handleNotFound() {
       return "404";
   }
   ```

2. **Global** (`@ControllerAdvice`):
   ```java
   @ControllerAdvice
   public class GlobalExceptionHandler {
       // Handle multiple controller exceptions
   }
   ```

3. **Default** (`BasicErrorController`):
   - Handles all uncaught exceptions
   - Routes to `/error`
   - Renders `error.html`
   - **CrashController** demonstrates this layer

**Error Attributes Available**:
| Attribute | Description | Example |
|-----------|-------------|---------|
| `timestamp` | When error occurred | 2025-01-09T12:34:56 |
| `status` | HTTP status code | 500 |
| `error` | Error reason phrase | Internal Server Error |
| `message` | Exception message | Expected: controller used... |
| `path` | Request path | /oups |
| `trace` | Stack trace | java.lang.RuntimeException... |

**Production Configuration**:
```properties
# application-prod.properties
server.error.include-message=always
server.error.include-binding-errors=never
server.error.include-stacktrace=never
server.error.include-exception=false
server.error.whitelabel.enabled=false
```

**Custom Error Page**:
```html
<!-- templates/error.html -->
<div th:if="${status == 404}">
    <h1>Page Not Found</h1>
</div>
<div th:if="${status == 500}">
    <h1>Internal Server Error</h1>
</div>
```

---

### 6. Testing Strategies

**Configuration Testing**:
```java
@SpringBootTest
class CacheConfigurationTests {
    @Autowired
    private CacheManager cacheManager;
    
    @Test
    void testVetsCacheExists() {
        Cache cache = cacheManager.getCache("vets");
        assertNotNull(cache);
    }
    
    @Test
    void testCacheStatisticsEnabled() {
        // Verify JMX statistics available
    }
}
```

**Controller Unit Testing**:
```java
@WebMvcTest(WelcomeController.class)
class WelcomeControllerTests {
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void testWelcomePage() throws Exception {
        mockMvc.perform(get("/"))
            .andExpect(status().isOk())
            .andExpect(view().name("welcome"));
    }
}

@WebMvcTest(CrashController.class)
class CrashControllerTests {
    @Test
    void testCrashController() throws Exception {
        mockMvc.perform(get("/oups"))
            .andExpect(status().is5xxServerError());
    }
}
```

**Internationalization Testing**:
```java
@SpringBootTest
@AutoConfigureMockMvc
class InternationalizationTests {
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void testLanguageSwitchToSpanish() throws Exception {
        mockMvc.perform(get("/").param("lang", "es"))
            .andExpect(status().isOk())
            .andExpect(content().string(containsString("Bienvenido")));
    }
    
    @Test
    void testLocalePersistedInSession() throws Exception {
        MockHttpSession session = new MockHttpSession();
        
        // Set locale
        mockMvc.perform(get("/?lang=es").session(session));
        
        // Verify persistence
        mockMvc.perform(get("/").session(session))
            .andExpect(content().string(containsString("Bienvenido")));
    }
}
```

---

## Common Pitfalls & Solutions

### Pitfall 1: Cache Not Working

**Problem**: `@Cacheable` annotation has no effect

**Causes**:
1. `@EnableCaching` missing
2. Method not public
3. Internal method calls (same class)

**Solution**:
```java
// WRONG
class VetService {
    public Collection<Vet> getAllVets() {
        return findAll();  // Internal call bypasses proxy
    }
    
    @Cacheable("vets")
    Collection<Vet> findAll() {  // Not public
        return vetRepository.findAll();
    }
}

// CORRECT
@Service
public class VetService {
    @Cacheable("vets")
    public Collection<Vet> findAll() {  // Public method
        return vetRepository.findAll();
    }
}
```

---

### Pitfall 2: Locale Not Persisting

**Problem**: Language resets after each request

**Cause**: LocaleResolver not in session scope or session not maintained

**Solution**:
```java
// Ensure SessionLocaleResolver is used
@Bean
public LocaleResolver localeResolver() {
    SessionLocaleResolver resolver = new SessionLocaleResolver();
    resolver.setDefaultLocale(Locale.ENGLISH);
    return resolver;  // Must be registered as bean
}
```

**Verify Session Cookies**:
- Check browser stores `JSESSIONID` cookie
- Ensure cookies not blocked

---

### Pitfall 3: Error Page Not Customizing

**Problem**: Still seeing default Whitelabel error page

**Causes**:
1. `error.html` not in `templates/` directory
2. Template engine misconfigured
3. `server.error.whitelabel.enabled=true` overriding

**Solution**:
```
src/main/resources/templates/error.html  ✓ Correct location
src/main/resources/static/error.html     ✗ Wrong (static resources)
src/main/resources/error.html            ✗ Wrong (not in templates)
```

---

### Pitfall 4: Message Keys Not Resolving

**Problem**: Page displays `??owner.lastName_en??` instead of "Last Name"

**Causes**:
1. Missing message key in properties file
2. Typo in key name
3. Properties file encoding issue (non-ASCII characters)

**Solution**:
```properties
# Ensure keys exist in all language files
# messages.properties
owner.lastName=Last Name

# messages_es.properties
owner.lastName=Apellido

# For special characters, use Unicode escapes or UTF-8 encoding
owner.name=Propriétaire  # May need: Propri\u00E9taire
```

---

### Pitfall 5: Cache Statistics Not Available

**Problem**: JMX MBean for cache statistics not found

**Causes**:
1. Statistics not enabled
2. JCache implementation doesn't support statistics
3. JMX disabled

**Solution**:
```java
// Ensure statistics enabled
private javax.cache.configuration.Configuration<Object, Object> cacheConfiguration() {
    return new MutableConfiguration<>().setStatisticsEnabled(true);
}
```

**Enable JMX** (enabled by default):
```properties
spring.jmx.enabled=true
```

---

## Performance Considerations

### Cache Performance

**Without Caching** (database query every request):
```
Average response time: 150ms (database query: 120ms)
Database load: 100 queries/second for 100 req/s
```

**With Caching** (single database query, subsequent cache hits):
```
Average response time: 30ms (cache lookup: <1ms)
Database load: 1 query/hour (on cache expiration)
Performance improvement: 5x faster
```

**Cache Hit Rate Monitoring**:
- **Target**: >90% hit rate for reference data like vets
- **Action**: If <80%, investigate cache eviction or sizing

### Session Storage Performance

**Locale in Session**:
- **Memory**: ~100 bytes per session for locale
- **Scalability**: For clustered deployments, use sticky sessions or externalize session store (Redis)

**Alternative for High Scale**:
```java
// Cookie-based locale (no server state)
@Bean
public LocaleResolver localeResolver() {
    CookieLocaleResolver resolver = new CookieLocaleResolver();
    resolver.setDefaultLocale(Locale.ENGLISH);
    resolver.setCookieName("locale");
    resolver.setCookieMaxAge(365 * 24 * 60 * 60);  // 1 year
    return resolver;
}
```

### Error Page Performance

**CrashController Impact**:
- Minimal - only accessed intentionally for testing
- Should be removed or secured in production
- Consider `@Profile("dev")` to disable in production

---

## Extension Points

### 1. Additional Caches

**Adding Pet Types Cache**:
```java
@Bean
public JCacheManagerCustomizer petclinicCacheConfigurationCustomizer() {
    return cm -> {
        cm.createCache("vets", cacheConfiguration());
        cm.createCache("petTypes", cacheConfiguration());  // New cache
    };
}

// Usage
@Cacheable("petTypes")
public List<PetType> findPetTypes() {
    return petTypeRepository.findAll();
}
```

---

### 2. Advanced Locale Handling

**Browser Locale Detection**:
```java
@Bean
public LocaleResolver localeResolver() {
    SessionLocaleResolver resolver = new SessionLocaleResolver();
    resolver.setDefaultLocale(Locale.ENGLISH);
    // If no session locale, use browser's Accept-Language
    resolver.setLocaleAttributeName("org.springframework.web.servlet.i18n.SessionLocaleResolver.LOCALE");
    return resolver;
}
```

**Time Zone Support**:
```java
@Bean
public LocaleResolver localeResolver() {
    SessionLocaleResolver resolver = new SessionLocaleResolver();
    resolver.setDefaultLocale(Locale.ENGLISH);
    resolver.setDefaultTimeZone(TimeZone.getTimeZone("UTC"));
    return resolver;
}
```

---

### 3. Health Checks and Monitoring

**Spring Boot Actuator Integration**:
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

**Cache Health Indicator**:
```java
@Component
public class CacheHealthIndicator implements HealthIndicator {
    @Autowired
    private CacheManager cacheManager;
    
    @Override
    public Health health() {
        Cache vetsCache = cacheManager.getCache("vets");
        if (vetsCache != null) {
            return Health.up()
                .withDetail("vetsCache", "available")
                .build();
        }
        return Health.down()
            .withDetail("vetsCache", "missing")
            .build();
    }
}
```

---

### 4. Custom Error Controllers

**Specific Error Pages**:
```java
@Controller
public class CustomErrorController implements ErrorController {
    @RequestMapping("/error")
    public String handleError(HttpServletRequest request) {
        Integer statusCode = (Integer) request.getAttribute(
            "javax.servlet.error.status_code");
        
        if (statusCode == 404) {
            return "error/404";
        } else if (statusCode == 403) {
            return "error/403";
        }
        return "error/generic";
    }
}
```

---

## Security Considerations

### 1. Error Information Disclosure

**Risk**: Exception details expose system internals

**Mitigation**:
```properties
# Production settings
server.error.include-stacktrace=never
server.error.include-message=on_param  # Only when ?trace=true
server.error.include-exception=false
```

---

### 2. Cache Poisoning

**Risk**: Cached malicious data served to users

**Mitigation**:
- Validate and sanitize data before caching
- Use cache only for read-only reference data
- Implement cache eviction on data changes

---

### 3. Session Fixation

**Risk**: Attacker sets session ID via `lang` parameter manipulation

**Mitigation**:
- `LocaleChangeInterceptor` is safe (doesn't affect session ID)
- Spring Security provides session fixation protection
- Validate locale parameter values

```java
// Enhanced security
@Bean
public LocaleChangeInterceptor localeChangeInterceptor() {
    LocaleChangeInterceptor interceptor = new LocaleChangeInterceptor();
    interceptor.setParamName("lang");
    // Only allow specific locales
    interceptor.setHttpMethods("GET", "POST");
    return interceptor;
}
```

---

## Summary

The `system` package is a well-designed infrastructure layer providing essential cross-cutting concerns:

**Key Strengths**:
- **Clear Separation**: Independent of business logic
- **Standards-Based**: Uses JCache API, Spring conventions
- **User-Friendly**: Easy language switching, friendly error pages
- **Observable**: Cache statistics, error logging
- **Extensible**: Easy to add caches, languages, configurations
- **Best Practices**: Configuration classes, package-private visibility, dependency injection

**Core Responsibilities**:
1. **Caching**: JCache configuration with monitoring
2. **Internationalization**: Multi-language support with session persistence
3. **Navigation**: Application home page
4. **Error Handling**: Demonstration and custom error pages

**Architectural Role**:
Foundation layer that all other packages depend on, providing infrastructure without coupling to business domain, following single responsibility and separation of concerns principles.

This package serves as an excellent reference for configuring Spring Boot infrastructure components.
