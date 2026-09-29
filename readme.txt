Readme

 - app.py: Desenvolvido em python 2.7 para conexão com a biblioteca Naoqi. O principal papel é receber e enviar comandos do NAO.
           Servidor Flask executado localmente - porta 5000
 - vision.py: Servidor Flask em python 3 para receber e converter as imagens capturados pelo NAO, emitindo streaming e frames para processamento de imagens
              Servidor Flask executado localmente - porta 5001
 - emotion.py: Servidor Flask em python 3.2 para rodar deep face, deep learning de processamento de imagens, para análise de expressões faciais

Fluxo de funcionamento:


ssh local no charizard:
ssh -L 5002:127.0.0.1:5002 -R 5001:127.0.0.1:5001 eliel@10.11.11.11  
ssh global no charizard:
ssh -L 5002:127.0.0.1:5002 -R 5001:127.0.0.1:5001 -p 21122 eliel@143.107.183.160 