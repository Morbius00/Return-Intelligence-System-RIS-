# Complete Pipeline Flow Diagram

## 1. High-Level System Flow

```mermaid
flowchart TD
    Start([User Input]) --> API[FastAPI Receives Request]
    API --> SpamCheck{Spam Detection}
    SpamCheck -->|Is Spam| ReturnSpam[Return: is_spam=True]
    SpamCheck -->|Not Spam| Preprocess[Text Preprocessing]
    Preprocess --> TFIDF[TF-IDF Vectorization]
    TFIDF --> Classifier[Logistic Regression]
    Classifier --> Severity[Severity Mapping]
    Severity --> Response[Format Response]
    ReturnSpam --> Response
    Response --> End([Return JSON to User])
    
    style Start fill:#CBFF63
    style End fill:#CBFF63
    style SpamCheck fill:#FFD700
    style Classifier fill:#87CEEB
```

## 2. Detailed Text Processing Pipeline

```mermaid
flowchart LR
    A[Raw Text:<br/>'Item ARRIVED broken!!'] --> B[Lowercase]
    B --> C[Remove Punctuation]
    C --> D[Remove Numbers]
    D --> E[Tokenize]
    E --> F[Remove Stopwords]
    F --> G[Lemmatization]
    G --> H[Filter Short Tokens]
    H --> I[Join Tokens]
    I --> J[Output:<br/>'item arrive broken']
    
    style A fill:#FFE4B5
    style J fill:#90EE90
```

## 3. Complete End-to-End Flow with Details

```mermaid
flowchart TD
    subgraph Input Layer
        A1[User/Client] --> A2[HTTP POST Request]
        A2 --> A3{Request Type?}
        A3 -->|Single| B1[/predict]
        A3 -->|Batch| B2[/predict/batch]
        A3 -->|Sheets| B3[/sheets/update]
    end
    
    subgraph API Layer
        B1 --> C1[Validate Input]
        B2 --> C1
        B3 --> C1
        C1 --> C2{Model Loaded?}
        C2 -->|No| ERR1[Return 503 Error]
        C2 -->|Yes| D1[Extract Text]
    end
    
    subgraph Processing Layer
        D1 --> E1{Spam Check}
        E1 -->|Yes| E2[Mark as Spam]
        E1 -->|No| F1[Preprocess Text]
        F1 --> F2[Lowercase]
        F2 --> F3[Remove Punctuation]
        F3 --> F4[Tokenize]
        F4 --> F5[Remove Stopwords]
        F5 --> F6[Lemmatize]
        F6 --> F7[Clean Tokens]
        F7 --> G1[TF-IDF Vectorization]
        G1 --> G2[1000-D Vector]
        G2 --> H1[Logistic Regression]
        H1 --> H2[Predict Category]
        H2 --> H3[Get Confidence]
        H3 --> I1{Confidence > 0.4?}
        I1 -->|No| I2[Category: Uncertain]
        I1 -->|Yes| I3[Use Predicted Category]
        I2 --> J1[Severity Mapping]
        I3 --> J1
        E2 --> J1
    end
    
    subgraph Output Layer
        J1 --> K1[Build Response]
        K1 --> K2[Add Metadata]
        K2 --> K3[Serialize to JSON]
        K3 --> L1[Return HTTP 200]
    end
    
    L1 --> M1[Client Receives Response]
    ERR1 --> M1
    
    style E1 fill:#FFD700
    style H1 fill:#87CEEB
    style I1 fill:#FFD700
    style J1 fill:#98FB98
    style M1 fill:#CBFF63
```

## 4. Spam Detection Flow

```mermaid
flowchart TD
    A[Input Text] --> B{Empty or Whitespace?}
    B -->|Yes| SPAM1[SPAM: Empty]
    B -->|No| C{Length < 3 chars?}
    C -->|Yes| SPAM2[SPAM: Too Short]
    C -->|No| D{Exact Match<br/>Spam Phrases?}
    D -->|Yes| SPAM3[SPAM: Known Pattern]
    D -->|No| E{Contains<br/>Spam Substring?}
    E -->|Yes| SPAM4[SPAM: Spam Keyword]
    E -->|No| F{>70% Same<br/>Character?}
    F -->|Yes| SPAM5[SPAM: Repetitive]
    F -->|No| VALID[NOT SPAM ✓]
    
    SPAM1 --> RESULT[Return is_spam=True]
    SPAM2 --> RESULT
    SPAM3 --> RESULT
    SPAM4 --> RESULT
    SPAM5 --> RESULT
    VALID --> CONTINUE[Continue Processing]
    
    style SPAM1 fill:#FF6B6B
    style SPAM2 fill:#FF6B6B
    style SPAM3 fill:#FF6B6B
    style SPAM4 fill:#FF6B6B
    style SPAM5 fill:#FF6B6B
    style VALID fill:#90EE90
```

## 5. Machine Learning Classification Flow

```mermaid
flowchart LR
    subgraph Input
        A[Text Vector<br/>1000 dimensions]
    end
    
    subgraph Logistic Regression Model
        B1[Binary Classifier 1:<br/>Product Quality]
        B2[Binary Classifier 2:<br/>Expiry Issue]
        B3[Binary Classifier 3:<br/>Packaging Issue]
        B4[Binary Classifier 4:<br/>Wrong Item]
        B5[Binary Classifier 5:<br/>Customer Preference]
        B6[Binary Classifier 6:<br/>Other]
    end
    
    subgraph Probabilities
        C1[P1 = 0.87]
        C2[P2 = 0.04]
        C3[P3 = 0.18]
        C4[P4 = 0.05]
        C5[P5 = 0.02]
        C6[P6 = 0.01]
    end
    
    subgraph Decision
        D[Select Max Probability]
        E[Product Quality Issue<br/>Confidence: 0.87]
    end
    
    A --> B1 --> C1
    A --> B2 --> C2
    A --> B3 --> C3
    A --> B4 --> C4
    A --> B5 --> C5
    A --> B6 --> C6
    
    C1 --> D
    C2 --> D
    C3 --> D
    C4 --> D
    C5 --> D
    C6 --> D
    
    D --> E
    
    style C1 fill:#90EE90
    style E fill:#CBFF63
```

## 6. Batch Processing Workflow

```mermaid
flowchart TD
    A[Start Batch Process] --> B{Input Type?}
    B -->|CSV| C1[Read CSV File]
    B -->|Google Sheets| C2[Read Google Sheet]
    
    C1 --> D[Extract Return Reasons]
    C2 --> D
    
    D --> E[Create Empty Results List]
    E --> F[For Each Reason]
    
    F --> G[Process Single Reason]
    G --> H[Spam Check]
    H --> I[Preprocess]
    I --> J[TF-IDF]
    J --> K[Classify]
    K --> L[Add to Results]
    
    L --> M{More Reasons?}
    M -->|Yes| F
    M -->|No| N[Compile Results]
    
    N --> O{Output Type?}
    O -->|CSV| P1[Write to New CSV]
    O -->|Google Sheets| P2[Update Sheet<br/>Add New Columns]
    
    P1 --> Q[Generate Statistics]
    P2 --> Q
    Q --> R[Log Summary]
    R --> S[End]
    
    style A fill:#CBFF63
    style G fill:#87CEEB
    style S fill:#90EE90
```

## 7. Google Sheets Integration Flow

```mermaid
flowchart TD
    A[API Request] --> B[Validate Spreadsheet ID]
    B --> C[Load Service Account Credentials]
    C --> D{Credentials Valid?}
    D -->|No| ERR1[Return Auth Error]
    D -->|Yes| E[Authenticate with Google API]
    E --> F[Open Spreadsheet]
    F --> G{Sheet Exists?}
    G -->|No| ERR2[Return Sheet Not Found]
    G -->|Yes| H[Read Sheet Data]
    H --> I[Extract Return Reasons]
    I --> J[Batch Classify All Reasons]
    J --> K[Format Results]
    K --> L[Add New Columns<br/>reason_category<br/>severity_score<br/>is_spam]
    L --> M[Update Sheet via API]
    M --> N[Return Success Response]
    
    style E fill:#4285F4
    style M fill:#90EE90
    style ERR1 fill:#FF6B6B
    style ERR2 fill:#FF6B6B
```

## 8. Training Pipeline

```mermaid
flowchart TD
    A[training_data/sample_data.csv] --> B[Load CSV with pandas]
    B --> C[Validate Columns<br/>return_reason, category]
    C --> D[Remove NaN values]
    D --> E[Split Data<br/>80% Train / 20% Test]
    E --> F[Preprocess All Texts]
    
    F --> G[Train TF-IDF Vectorizer<br/>on Training Data]
    G --> H[Transform Training Data<br/>to Vectors]
    G --> I[Transform Test Data<br/>to Vectors]
    
    H --> J[Train Logistic Regression<br/>on Training Vectors]
    J --> K[Evaluate on Test Set]
    K --> L[Calculate Metrics<br/>Accuracy, Precision, Recall]
    L --> M[Print Classification Report]
    
    J --> N[Save model.pkl]
    G --> O[Save tfidf.pkl]
    
    N --> P[Models Ready for API]
    O --> P
    
    style A fill:#FFE4B5
    style P fill:#90EE90
```

## 9. API Startup Sequence

```mermaid
sequenceDiagram
    participant User
    participant Terminal
    participant Uvicorn
    participant FastAPI
    participant Classifier
    participant SheetsService
    
    User->>Terminal: python -m uvicorn app.main:app --reload
    Terminal->>Uvicorn: Start Server
    Uvicorn->>FastAPI: Initialize Application
    
    FastAPI->>FastAPI: Load Environment Variables
    FastAPI->>Classifier: Load model.pkl and tfidf.pkl
    
    alt Models Found
        Classifier-->>FastAPI: Models Loaded Successfully ✓
    else Models Not Found
        Classifier-->>FastAPI: Warning: Models Not Found
    end
    
    FastAPI->>SheetsService: Initialize with Credentials
    
    alt Credentials Found
        SheetsService->>SheetsService: Authenticate with Google
        SheetsService-->>FastAPI: Service Ready ✓
    else Credentials Not Found
        SheetsService-->>FastAPI: Warning: Sheets Unavailable
    end
    
    FastAPI-->>Uvicorn: Application Ready
    Uvicorn-->>Terminal: Server Running on http://0.0.0.0:8000
    Terminal-->>User: API Ready for Requests
```

## 10. Single Prediction Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant SpamDetector
    participant Preprocessor
    participant Vectorizer
    participant Model
    participant SeverityMapper
    
    Client->>API: POST /predict<br/>{"return_reason": "item broken"}
    API->>API: Validate Request
    
    API->>SpamDetector: is_spam("item broken")
    SpamDetector-->>API: False ✓
    
    API->>Preprocessor: preprocess_text("item broken")
    Preprocessor->>Preprocessor: lowercase → tokenize → lemmatize
    Preprocessor-->>API: "item broken"
    
    API->>Vectorizer: transform("item broken")
    Vectorizer-->>API: [0.42, 0.65, 0, ..., 0] (1000-D)
    
    API->>Model: predict(vector)
    Model->>Model: Compute probabilities
    Model-->>API: "Product Quality Issue" (0.87)
    
    API->>SeverityMapper: get_severity("Product Quality Issue")
    SeverityMapper-->>API: 0.9
    
    API->>API: Build Response JSON
    API-->>Client: 200 OK<br/>{<br/>  "is_spam": false,<br/>  "reason_category": "Product Quality Issue",<br/>  "severity_score": 0.9,<br/>  "confidence": 0.87<br/>}
```

## 11. System Architecture Layers

```mermaid
graph TB
    subgraph Client Layer
        A1[Web Browser<br/>index.html]
        A2[REST Client<br/>curl/Postman]
        A3[Python Script<br/>requests library]
        A4[Google Sheets<br/>Integration]
    end
    
    subgraph API Layer
        B1[FastAPI Application<br/>app/main.py]
        B2[Endpoints:<br/>/predict<br/>/predict/batch<br/>/sheets/update]
        B3[CORS Middleware]
        B4[Request Validation<br/>Pydantic Models]
    end
    
    subgraph Business Logic Layer
        C1[NLP Classifier<br/>classifier.py]
        C2[Spam Detector<br/>spam_detector.py]
        C3[Text Preprocessor<br/>preprocess.py]
        C4[Google Sheets Service<br/>sheets_service.py]
    end
    
    subgraph ML Layer
        D1[TF-IDF Vectorizer<br/>scikit-learn]
        D2[Logistic Regression<br/>scikit-learn]
        D3[NLTK Components<br/>tokenizer, lemmatizer]
    end
    
    subgraph Data Layer
        E1[(Trained Models<br/>model.pkl<br/>tfidf.pkl)]
        E2[(Training Data<br/>sample_data.csv)]
        E3[(Google Sheets API)]
    end
    
    A1 & A2 & A3 & A4 --> B1
    B1 --> B2 & B3 & B4
    B2 --> C1 & C2 & C3 & C4
    C1 & C2 & C3 --> D1 & D2 & D3
    C4 --> E3
    D1 & D2 --> E1
    
    style B1 fill:#87CEEB
    style C1 fill:#98FB98
    style D2 fill:#FFD700
    style E1 fill:#FFE4B5
```

## 12. Data Flow - Single Prediction

```mermaid
flowchart LR
    A[User Input:<br/>'Item broken'] --> B[API Endpoint]
    B --> C[Spam Check]
    C --> D[Preprocess:<br/>'item broken']
    D --> E[TF-IDF:<br/>Vector 1000-D]
    E --> F[Classifier:<br/>Logistic Regression]
    F --> G[Prediction:<br/>Product Quality]
    G --> H[Severity:<br/>0.9]
    H --> I[JSON Response]
    I --> J[User]
    
    style A fill:#CBFF63
    style F fill:#87CEEB
    style I fill:#90EE90
```

## 13. Component Interactions

```mermaid
graph LR
    UI[User Interface] -->|HTTP Request| API[FastAPI]
    API -->|Text| SPAM[Spam Detector]
    SPAM -->|Clean Text| PREP[Preprocessor]
    PREP -->|Processed Text| TFIDF[TF-IDF]
    TFIDF -->|Vector| LR[Logistic Regression]
    LR -->|Category| SEV[Severity Mapper]
    SEV -->|Final Result| API
    API -->|JSON| UI
    
    API -->|Read/Write| GS[Google Sheets Service]
    GS -->|API Calls| GAPI[Google Sheets API]
    
    TRAIN[Training Script] -->|Builds| LR
    TRAIN -->|Builds| TFIDF
    TRAIN -->|Reads| TD[Training Data]
    
    style API fill:#87CEEB
    style LR fill:#FFD700
    style TRAIN fill:#98FB98
```

---

## Diagram Notes

### Mermaid Rendering

These diagrams use Mermaid syntax and can be rendered in:
- GitHub (native support)
- VS Code (with Mermaid extension)
- Online: https://mermaid.live/
- Documentation sites (GitBook, MkDocs, etc.)

### Color Legend

- 🟢 **Green (#90EE90)**: Success/Output
- 🔵 **Blue (#87CEEB)**: Processing/ML
- 🟡 **Yellow (#FFD700)**: Decision Points
- 🟠 **Orange (#FFE4B5)**: Input/Data
- 🔴 **Red (#FF6B6B)**: Errors/Spam
- 🟣 **Lime (#CBFF63)**: User Interface

---

*These diagrams provide visual representation of the system architecture and data flow. Use them alongside COMPLETE_DOCUMENTATION.md for full understanding.*
