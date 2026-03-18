from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session
from database import get_session
from models import QueryRequest
from repository import ChatRepository
from service import PortfolioAIService

router = APIRouter(prefix="/portfolio", tags=["AI Portfolio"])

def get_ai_service(session: Session = Depends(get_session)):
    repo = ChatRepository(session)
    return PortfolioAIService(repo)

@router.post("/chat")
def chat_com_portfolio(
    request: Request, 
    query: QueryRequest, 
    service: PortfolioAIService = Depends(get_ai_service)
):
    ip_visitante = request.client.host
    
    navegador = request.headers.get('user-agent')
    print(f"Novo acesso do IP: {ip_visitante} usando {navegador}")
    try:
        resposta = service.processar_mensagem(
            session_id=query.session_id, 
            user_message=query.message,
            model_name=query.model_choice.value
        )
        
        return {
            "session_id": query.session_id,
            "model_used": query.model_choice,
            "response": resposta
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor da IA: {str(e)}")

@router.get("/historico/{session_id}")
def obter_historico(session_id: str, session: Session = Depends(get_session)):
    repo = ChatRepository(session)
    historico = repo.get_history(session_id)
    
    if not historico:
        raise HTTPException(status_code=404, detail="Nenhum histórico encontrado para esta sessão.")
        
    return historico