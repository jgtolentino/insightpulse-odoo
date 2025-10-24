import os
import asyncio
import psycopg2
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Load environment variables
load_dotenv()

app = FastAPI(title="Odoo LangChain BI Service", version="1.0.0")


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    sql_query: str
    results: str
    error: str = None


class OdooDatabaseTool:
    """Execute SQL queries on the Odoo PostgreSQL database"""
    
    def run(self, query: str) -> str:
        """Execute SQL query on Odoo database"""
        try:
            conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'postgres'),
                database=os.getenv('POSTGRES_DB', 'odoo'),
                user=os.getenv('POSTGRES_USER', 'odoo'),
                password=os.getenv('POSTGRES_PASSWORD', 'odoo'),
                port=os.getenv('POSTGRES_PORT', '5432')
            )
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Format results for better readability
            if results:
                columns = [desc[0] for desc in cursor.description]
                formatted_results = f"Columns: {columns}\n"
                formatted_results += "Results:\n"
                for row in results[:10]:  # Limit to first 10 rows
                    formatted_results += f"{row}\n"
                if len(results) > 10:
                    formatted_results += f"... and {len(results) - 10} more rows\n"
                return formatted_results
            else:
                return "No results found"
                
        except Exception as e:
            return f"Database error: {str(e)}"


class OdooSemanticTool:
    """Convert natural language questions about Odoo data into SQL queries using OpenAI"""
    
    def __init__(self):
        """Initialize the OpenAI LLM"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=api_key
        )
        
        # Define the prompt template for SQL generation
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SQL query generator for Odoo ERP database. 
Convert natural language questions into PostgreSQL SQL queries for Odoo database.

Common Odoo tables:
- sale_order (sales orders)
- account_invoice (invoices)
- res_partner (customers/vendors)
- purchase_order (purchase orders)
- product_product (products)
- hr_employee (employees)
- project_task (tasks)

Rules:
- Always use LIMIT 10 unless specified otherwise
- Use proper JOINs between related tables
- Include relevant columns like names, dates, amounts, status
- Return only the SQL query, no explanations
- Use PostgreSQL syntax
- Handle date filtering appropriately
- Use meaningful column aliases
            """),
            ("human", "{question}")
        ])
    
    def run(self, question: str) -> str:
        """Convert natural language to SQL for Odoo data using OpenAI"""
        try:
            # Generate SQL using OpenAI
            prompt = self.prompt_template.format_messages(question=question)
            response = self.llm.invoke(prompt)
            sql_query = response.content.strip()
            
            # Clean up the SQL query
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            sql_query = sql_query.strip()
            
            return sql_query
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fallback to simple semantic mapping
            return self._fallback_semantic_mapping(question)
    
    def _fallback_semantic_mapping(self, question: str) -> str:
        """Fallback semantic mapping for when OpenAI API fails"""
        question_lower = question.lower()
        
        # Simple semantic mapping for common Odoo queries
        if "sales" in question_lower and "order" in question_lower:
            return """
            SELECT 
                so.name as order_number,
                so.date_order,
                rp.name as customer,
                so.amount_total as total_amount,
                so.state
            FROM sale_order so
            JOIN res_partner rp ON so.partner_id = rp.id
            ORDER BY so.date_order DESC
            LIMIT 10
            """
        elif "invoice" in question_lower:
            return """
            SELECT 
                ai.number as invoice_number,
                ai.date_invoice,
                rp.name as partner,
                ai.amount_total,
                ai.state
            FROM account_invoice ai
            JOIN res_partner rp ON ai.partner_id = rp.id
            ORDER BY ai.date_invoice DESC
            LIMIT 10
            """
        elif "vendor" in question_lower or "supplier" in question_lower:
            return """
            SELECT 
                rp.name as vendor_name,
                rp.email,
                rp.phone,
                COUNT(po.id) as purchase_order_count
            FROM res_partner rp
            LEFT JOIN purchase_order po ON rp.id = po.partner_id
            WHERE rp.supplier = true
            GROUP BY rp.id, rp.name, rp.email, rp.phone
            ORDER BY purchase_order_count DESC
            LIMIT 10
            """
        else:
            return """
            SELECT 
                'Please be more specific about what Odoo data you want to query.' as message,
                'Try asking about sales, invoices, vendors, projects, or employees.' as suggestion
            """


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Odoo LangChain BI Service",
        "version": "1.0.0",
        "description": "Natural language to SQL conversion for Odoo data",
        "endpoints": {
            "/query": "POST - Convert natural language questions to SQL and execute",
            "/health": "GET - Service health check"
        }
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Convert natural language question to SQL and execute it"""
    try:
        # Use the semantic tool to generate SQL
        semantic_tool = OdooSemanticTool()
        sql_query = semantic_tool.run(request.question)
        
        # Execute the query
        db_tool = OdooDatabaseTool()
        results = db_tool.run(sql_query)
        
        return QueryResponse(
            sql_query=sql_query,
            results=results
        )
        
    except Exception as e:
        return QueryResponse(
            sql_query="",
            results="",
            error=f"Error processing query: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_tool = OdooDatabaseTool()
        test_result = db_tool.run("SELECT 1")
        
        # Test OpenAI connection
        semantic_tool = OdooSemanticTool()
        
        return {
            "status": "healthy",
            "database": "connected",
            "openai": "configured"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Service unhealthy: {str(e)}")


if __name__ == "__main__":
    port = int(os.getenv('SERVICE_PORT', 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
