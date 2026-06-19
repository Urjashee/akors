#### Install requirements
```
uv pip install -r requirements.txt
```

#### Migrate tables
```text
uv run manage.py makemigrations accounts
uv run manage.py migrate
```

#### Run application
```text
uv run manage.py runserver
```

#### Container access
```text
docker exec -it akors-backend-web-1 bash
```

```text
 Steps to activate (manual)                                                                                                                                                        
                                                                                                                                                                                    
  1. Add your OpenAI key to .env:                                                                                                                                                   
  OPENAI_API_KEY=sk-...                                                                                                                                                             
                                                                                                                                                                                    
  2. Enable PGVector in your PostgreSQL database (run once):                                                                                                                        
  CREATE EXTENSION IF NOT EXISTS vector;                                                                                                                                            
                                                                                                                                                                                    
  3. Install dependencies:                                                                                                                                                          
  uv add langchain langchain-openai langchain-community langchain-postgres pypdf pgvector "psycopg[binary]"                                                                         
                                                                                                                                                                                    
  4. Run migrations:                                                                                                                                                                
  uv run manage.py makemigrations chatbot                                                                                                                                           
  uv run manage.py migrate chatbot                                                                                                                                                  
                                                                                                                                                                                    
  5. Place PDFs in documents/ at project root, then ingest:                                                                                                                         
  uv run manage.py ingest_documents                                                                                                                                                 
                                                                                                                                                                                    
  6. Test:                                                                                                                                                                          
  POST /api/chat/                                                                                                                                                                   
  Authorization: Bearer <token>                                                                                                                                                     
  {"question": "What is the cancellation policy?"}

```