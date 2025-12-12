# AI Persona Customer Survey - Code Flow Documentation

This document provides detailed code flow diagrams for each URI and workflow in the application.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Authentication Flow](#authentication-flow)
- [User Profile Flow](#user-profile-flow)
- [Analysis Upload Flow](#analysis-upload-flow)
- [Admin Dashboard Flow](#admin-dashboard-flow)
- [Dashboard View Flow](#dashboard-view-flow)

---

## Architecture Overview

```mermaid
graph TB
    Client[Client Browser]
    Router[FastAPI Routers]
    Auth[Auth Dependencies]
    Service[Services Layer]
    Repo[Repositories Layer]
    DB[(PostgreSQL Database)]
    
    Client --> Router
    Router --> Auth
    Auth --> Service
    Service --> Repo
    Repo --> DB
    
    style Client fill:#e1f5ff
    style Router fill:#fff4e1
    style Auth fill:#ffe1e1
    style Service fill:#e1ffe1
    style Repo fill:#f0e1ff
    style DB fill:#ffe1f0
```

---

## Authentication Flow

### URI: `/login/google` → `/rest/oauth2-credential/callback`

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant AuthRouter
    participant Google
    participant UserService
    participant UserRepo
    participant DB
    participant JWTHandler
    
    User->>Browser: Click "Login with Google"
    Browser->>AuthRouter: GET /login/google
    AuthRouter->>Browser: Redirect to Google OAuth
    Browser->>Google: Authorization Request
    Google->>User: Login & Consent
    User->>Google: Approve
    Google->>Browser: Redirect with code
    Browser->>AuthRouter: GET /rest/oauth2-credential/callback?code=...
    
    AuthRouter->>Google: POST /token (exchange code)
    Google->>AuthRouter: access_token
    AuthRouter->>Google: GET /userinfo (with token)
    Google->>AuthRouter: User Info (email, name, picture)
    
    AuthRouter->>UserService: get_or_create_user(email, name, picture)
    UserService->>UserRepo: get_user_by_email(email)
    UserRepo->>DB: SELECT * FROM users WHERE email = ?
    
    alt User Exists
        DB->>UserRepo: User Record
        UserRepo->>UserService: User Data
    else User Not Found
        UserRepo->>DB: INSERT INTO users (email, name, picture, role='MEMBER')
        DB->>UserRepo: New User Record
        UserRepo->>UserService: New User Data
    end
    
    UserService->>AuthRouter: User Data
    AuthRouter->>JWTHandler: create_access_token(user_data)
    JWTHandler->>AuthRouter: JWT Token
    AuthRouter->>Browser: Redirect to /dashboard + Set Cookie (access_token)
    Browser->>User: Display Dashboard
```

**Files Involved:**
- [auth_router.py](file:///apps/project_AI_Persona_CustomerSurvey/app/routers/auth_router.py) - OAuth callback and login endpoints
- [users_service.py](file:///apps/project_AI_Persona_CustomerSurvey/app/services/users_service.py) - User business logic
- [users_repository.py](file:///apps/project_AI_Persona_CustomerSurvey/app/repositories/users_repository.py) - Database operations
- [jwt_handler.py](file:///apps/project_AI_Persona_CustomerSurvey/app/auth/jwt_handler.py) - JWT token creation/verification

---

## User Profile Flow

### URI: `/user/profile`

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant UserRouter
    participant AuthDep
    participant JWTHandler
    participant DB
    participant Template
    
    User->>Browser: Navigate to /user/profile
    Browser->>UserRouter: GET /user/profile (with cookie)
    
    UserRouter->>AuthDep: get_current_user()
    AuthDep->>Browser: Extract access_token from cookie
    AuthDep->>JWTHandler: verify_token(token)
    
    alt Valid Token
        JWTHandler->>AuthDep: User Payload (sub, email, role, name, picture)
        AuthDep->>UserRouter: User Data
    else Invalid/Missing Token
        JWTHandler->>AuthDep: None/Error
        AuthDep->>Browser: 401 Unauthorized
    end
    
    UserRouter->>DB: SELECT * FROM analysis_results WHERE user_id = ?
    DB->>UserRouter: Analysis History
    
    UserRouter->>Template: Render profile.html (user, history)
    Template->>Browser: HTML Response
    Browser->>User: Display Profile Page
```

**Files Involved:**
- [user_router.py](file:///apps/project_AI_Persona_CustomerSurvey/app/routers/user_router.py) - Profile endpoint
- [auth.py](file:///apps/project_AI_Persona_CustomerSurvey/app/dependencies/auth.py) - Authentication dependency
- [db_connection.py](file:///apps/project_AI_Persona_CustomerSurvey/app/dependencies/db_connection.py) - Database connection
- [profile.html](file:///apps/project_AI_Persona_CustomerSurvey/app/templates/profile.html) - Profile template

---

## Analysis Upload Flow

### URI: `/api/analysis/upload`

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant AnalysisRouter
    participant AuthDep
    participant AnalysisService
    participant FileSystem
    participant DB
    
    User->>Browser: Upload CSV File
    Browser->>AnalysisRouter: POST /api/analysis/upload (file, cookie)
    
    AnalysisRouter->>AuthDep: get_current_user()
    AuthDep->>AnalysisRouter: User Data (or 401)
    
    AnalysisRouter->>AnalysisRouter: Validate file extension (.csv)
    
    alt Invalid File
        AnalysisRouter->>Browser: 400 Bad Request
    else Valid File
        AnalysisRouter->>AnalysisService: process_csv(file, user, conn)
        
        AnalysisService->>AnalysisService: Generate unique filename (UUID)
        AnalysisService->>FileSystem: Save file to /app/static/files/
        AnalysisService->>AnalysisService: Read CSV into DataFrame
        
        Note over AnalysisService: Data Processing Pipeline
        AnalysisService->>AnalysisService: 1. Fill missing values
        AnalysisService->>AnalysisService: 2. Encode categorical variables
        AnalysisService->>AnalysisService: 3. Select numeric features
        AnalysisService->>AnalysisService: 4. Scale features (StandardScaler)
        AnalysisService->>AnalysisService: 5. Find optimal K (silhouette score)
        AnalysisService->>AnalysisService: 6. KMeans clustering
        AnalysisService->>AnalysisService: 7. Generate personas from clusters
        
        AnalysisService->>DB: INSERT INTO analysis_results (user_id, filename, filelink, result)
        DB->>AnalysisService: Success
        
        AnalysisService->>AnalysisRouter: Analysis Result (clusters, personas, total_users)
        AnalysisRouter->>Browser: JSON Response
        Browser->>User: Display Results
    end
```

**Files Involved:**
- [analysis_router.py](file:///apps/project_AI_Persona_CustomerSurvey/app/routers/analysis_router.py) - Upload endpoint
- [analysis_service.py](file:///apps/project_AI_Persona_CustomerSurvey/app/services/analysis_service.py) - ML processing logic
- [auth.py](file:///apps/project_AI_Persona_CustomerSurvey/app/dependencies/auth.py) - Authentication dependency

**Data Processing Steps:**
1. **Preprocessing**: Fill missing values with 0
2. **Encoding**: Convert categorical variables using LabelEncoder
3. **Feature Selection**: Extract numeric features (exclude user_id)
4. **Scaling**: Standardize features using StandardScaler
5. **Clustering**: KMeans with optimal K (3-7 clusters, selected by silhouette score)
6. **Persona Generation**: Create persona profiles from cluster statistics
7. **Persistence**: Save results to database with file link

---

## Admin Dashboard Flow

### URI: `/admin/dashboard`

```mermaid
sequenceDiagram
    participant Admin
    participant Browser
    participant AdminRouter
    participant AuthDep
    participant JWTHandler
    participant DB
    participant Template
    
    Admin->>Browser: Navigate to /admin/dashboard
    Browser->>AdminRouter: GET /admin/dashboard (with cookie)
    
    AdminRouter->>AuthDep: get_current_admin()
    AuthDep->>AuthDep: get_current_user()
    AuthDep->>JWTHandler: verify_token(token)
    
    alt Valid Token
        JWTHandler->>AuthDep: User Payload
        
        alt User Role = ADMIN
            AuthDep->>AdminRouter: Admin User Data
        else User Role != ADMIN
            AuthDep->>Browser: 403 Forbidden
        end
    else Invalid Token
        AuthDep->>Browser: 401 Unauthorized
    end
    
    AdminRouter->>DB: SELECT COUNT(*) FROM users
    DB->>AdminRouter: users_count
    
    AdminRouter->>DB: SELECT * FROM users ORDER BY id DESC LIMIT 50
    DB->>AdminRouter: members list
    
    AdminRouter->>Template: Render admin_dashboard.html (user, users_count, members)
    Template->>Browser: HTML Response
    Browser->>Admin: Display Admin Dashboard
```

**Files Involved:**
- [admin_router.py](file:///apps/project_AI_Persona_CustomerSurvey/app/routers/admin_router.py) - Admin dashboard endpoint
- [auth.py](file:///apps/project_AI_Persona_CustomerSurvey/app/dependencies/auth.py) - Admin authentication dependency
- [admin_dashboard.html](file:///apps/project_AI_Persona_CustomerSurvey/app/templates/admin_dashboard.html) - Admin template

**Authorization Levels:**
1. **Authentication Check**: Verify JWT token exists and is valid
2. **Role Check**: Verify user role is 'ADMIN'
3. **Data Access**: Fetch aggregated statistics and user list

---

## Dashboard View Flow

### URI: `/dashboard` and `/`

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant IndexRouter
    participant AuthDep
    participant JWTHandler
    participant Template
    
    User->>Browser: Navigate to / or /dashboard
    Browser->>IndexRouter: GET / or /dashboard (with optional cookie)
    
    IndexRouter->>AuthDep: get_optional_user()
    
    alt Cookie Exists
        AuthDep->>Browser: Extract access_token from cookie
        AuthDep->>JWTHandler: verify_token(token)
        
        alt Valid Token
            JWTHandler->>AuthDep: User Payload
            AuthDep->>IndexRouter: User Data
        else Invalid Token
            JWTHandler->>AuthDep: None
            AuthDep->>IndexRouter: None
        end
    else No Cookie
        AuthDep->>IndexRouter: None
    end
    
    IndexRouter->>Template: Render template (request, user or None)
    Template->>Browser: HTML Response (with/without user context)
    Browser->>User: Display Page
```

**Files Involved:**
- [index_router.py](file:///apps/project_AI_Persona_CustomerSurvey/app/routers/index_router.py) - Index and dashboard endpoints
- [auth.py](file:///apps/project_AI_Persona_CustomerSurvey/app/dependencies/auth.py) - Optional authentication
- [index.html](file:///apps/project_AI_Persona_CustomerSurvey/app/templates/index.html) - Landing page template
- [dashboard.html](file:///apps/project_AI_Persona_CustomerSurvey/app/templates/dashboard.html) - Dashboard template

**Note**: These routes use `get_optional_user()` which allows both authenticated and unauthenticated access. The template can conditionally render content based on user presence.

---

## Database Schema

```mermaid
erDiagram
    users ||--o{ analysis_results : creates
    
    users {
        int id PK
        string email UK
        string name
        string picture
        string role
        timestamp created_at
    }
    
    analysis_results {
        int id PK
        int user_id FK
        string filename
        string filelink
        json result
        timestamp created_at
    }
```

---

## Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (asyncpg)
- **Authentication**: Google OAuth2 + JWT
- **ML Libraries**: scikit-learn, pandas
- **Template Engine**: Jinja2
- **Clustering**: KMeans with silhouette score optimization

---

## Key Dependencies

### Authentication Flow
- `get_optional_user()`: Returns user or None (for public pages)
- `get_current_user()`: Returns user or raises 401 (for protected pages)
- `get_current_admin()`: Returns admin user or raises 403 (for admin pages)

### Database Connection
- `get_db_connection()`: Provides asyncpg connection with automatic cleanup

### Services
- `UserService`: User management (get or create)
- `AnalysisService`: CSV processing and ML analysis

---

## Environment Variables

Required environment variables (configured in `.env`):
- `GOOGLE_CLIENT_ID`: Google OAuth2 client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth2 client secret
- `GOOGLE_REDIRECT_URI`: OAuth2 callback URL
- `DB_HOST`: PostgreSQL host
- `DB_PORT`: PostgreSQL port
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `JWT_SECRET_KEY`: Secret key for JWT signing
- `JWT_ALGORITHM`: JWT algorithm (e.g., HS256)
