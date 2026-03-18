import os
from dotenv import load_dotenv 
load_dotenv()
AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION=os.getenv('AWS_DEFAULT_REGION')

from pathlib import Path
from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.bedrock import BedrockConverseModel, BedrockModelSettings
from pydantic_ai.messages import ModelRequest, ModelResponse, UserPromptPart, TextPart
from repository import ChatRepository
from models import ModelChoice

class PortfolioAIService:
    def __init__(self, repository: ChatRepository):
        self.repository = repository
        self.documentos_paths = [
            Path(r'C:\repositorio\portfolio_api\portifolio\documents\Currículo.pdf'),
            Path(r'C:\repositorio\portfolio_api\portifolio\documents\DESENVOLVIMENTO TECNOLÓGICO E INOVAÇÃO – PIBITI  2024-2025.pdf'),
            Path(r'C:\repositorio\portfolio_api\portifolio\documents\Documentação Microsserviço.pdf'),
            Path(r'C:\repositorio\portfolio_api\portifolio\documents\SIAD.pdf')
        ]
        

    def processar_mensagem(self, session_id: str, user_message: str, model_name: str) -> str:
        if model_name == ModelChoice.sonnet.value:
            texto_instrucao = f"Acima estão meu currículo e documentos de projetos. Por favor, leia-os. Agora, responda à seguinte pergunta do usuário: {user_message}"
            self.base_system_prompt = """Você é o assistente virtual inteligente do meu portfólio. 
Seu objetivo principal é responder perguntas sobre meus projetos e experiência profissional com base nos documentos fornecidos.
Se o usuário perguntar algo totalmente fora do contexto (como conhecimentos gerais, capitais, receitas, etc.), responda de forma breve e educada, mas puxe o assunto de volta para o meu portfólio."""
            model_settings = BedrockModelSettings(
            temperature=1.0,
            max_tokens=64000,
            bedrock_performance_configuration={
                "latency": "standard"
            },
            bedrock_additional_model_requests_fields={
                "thinking": {
                    "type": "enabled",  
                    "budget_tokens": 32000
                }
            }
        )

        elif model_name == ModelChoice.nova.value:
            texto_instrucao = f"Acima estão meu currículo e documentos de projetos. Por favor, leia-os. Agora, responda à seguinte pergunta do usuário: {user_message}"
            self.base_system_prompt = """Você é o assistente virtual inteligente do meu portfólio. 
Seu objetivo principal é responder perguntas sobre meus projetos e experiência profissional com base nos documentos fornecidos.
Se o usuário perguntar algo totalmente fora do contexto (como conhecimentos gerais, capitais, receitas, etc.), responda de forma breve e educada, mas puxe o assunto de volta para o meu portfólio."""
            model_settings = BedrockModelSettings(
                temperature=0.1,
                max_tokens=10000,
                bedrock_performance_configuration={
                    "latency": "optimized"
                }
            )
        
        elif model_name == ModelChoice.haiku.value:
            texto_instrucao = f"Responda à seguinte pergunta do usuário: {user_message}"
            self.base_system_prompt = "Você é um assistente de respostas rápidas."
            model_settings = BedrockModelSettings(
            temperature=1.0,
            max_tokens=4096,
            bedrock_performance_configuration={
                "latency": "standard"
            }
        )
        else:
            raise ValueError(f"Modelo desconhecido: {model_name}")

        model = BedrockConverseModel(model_name=model_name, settings=model_settings)
        agent = Agent(model=model, system_prompt=self.base_system_prompt)

        mensagens_salvas = self.repository.get_history(session_id)
        
        historico_ia = []
        for msg in mensagens_salvas:
            if msg.role == 'user':
                historico_ia.append(ModelRequest(parts=[UserPromptPart(content=msg.content)]))
            else:
                historico_ia.append(ModelResponse(parts=[TextPart(content=msg.content)]))

        input_data = []
        
        print(f"[{model_name}] Carregando {len(self.documentos_paths)} PDFs...")
        for pdf in self.documentos_paths:
            if pdf.exists():
                input_data.append(BinaryContent.from_path(pdf))
            else:
                print(f"AVISO: PDF não encontrado no caminho -> {pdf}")

        input_data.append(texto_instrucao)
        self.repository.save_message(session_id, "user", user_message, model_name)

        print(f"[{model_name}] Enviando dados para a AWS Bedrock. Aguarde (isso pode demorar minutos)...")
        
        try:
            # É provavelmente AQUI que o seu código está travando/demorando
            result = agent.run_sync(
                input_data, 
                model_settings=model_settings,
                message_history=historico_ia
            )
            print(f"[{model_name}] Resposta gerada com sucesso pela AWS!")
            resposta_ia = result.output
            
        except Exception as e:
            print(f"[{model_name}] ERRO NA AWS: {str(e)}")
            resposta_ia = f"Desculpe, ocorreu um erro ao consultar o modelo: {str(e)}"
            
        self.repository.save_message(session_id, "bot", resposta_ia, model_name)
        
        return resposta_ia