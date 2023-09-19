from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import paramiko
from pythonping import ping
import os
from dotenv import load_dotenv
load_dotenv()

hostname = os.getenv("HOST")
port = int(os.getenv("PORT"))
username = os.getenv("USER")
password = os.getenv("PASS")

router = APIRouter()

class UpdateServiceModel(BaseModel):
    service: int
    acao: int

@router.get("/get-services") 
def get_services():
    try:
        result = ping(hostname, count=1)
        result_str = str(result)  # Converte o resultado para uma string válida

        return [
            {
                "service": "Stage 101",
                "result": result_str
            },
            {
                "service": "No service",
                "result": "offline"
            }
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro: {str(e)}')


@router.post("/update-service")
def update_service(request: UpdateServiceModel):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname, port, username, password)

        command = ''
        command_mask = ''
        if request.acao == 1:
            command = 'cd clients/sislog && git pull origin develop'
            command_mask = 'pull executado com sucesso!'
        elif request.acao == 2:
            command = 'cd clients/sislog && yarn install'
            command_mask = 'yarn install executado com sucesso!'
        elif request.acao == 3:
            command = 'cd clients/sislog && yarn build'
            command_mask = 'yarn build executado com sucesso!'
        elif request.acao == 4:
            command = 'cd clients/sislog && pm2 restart app-sislog --update-env'
            command_mask = ' pm2 restart app-sislog executado com sucesso!'
        else:
            raise HTTPException(status_code=400, detail='Opção inválida, tente novamente!')

        _, stdout, _ = client.exec_command(command)
        output = stdout.read().decode().strip()
        status = stdout.channel.recv_exit_status()

        if status == 0:
            return {
                "command": command_mask,
                "output": output
            }
        else:
            raise HTTPException(status_code=500, detail="O comando falhou, tente novamente!")

    except paramiko.SSHException as e:
        raise HTTPException(status_code=400, detail=f'Erro na execução do comando SSH: {str(e)}')

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Erro geral: {str(e)}')

    finally:
        client.close()
