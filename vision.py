from flask import Flask, request, Response, jsonify
import numpy as np
import cv2
import base64
import time

app = Flask(__name__)

# Variável global para armazenar o último frame recebido
latest_frame = None
status_cam = None
frame_bytes = None

@app.route('/frame', methods=['POST'])
def process_frame():
    global status_cam
    data = request.json
    width = data['width']
    height = data['height']
    img_data = base64.b64decode(data['image'])
    status_cam = data['status']
    #receive_frame(width,height,img_data)

    sucesso, msg = receive_frame(width, height, img_data)
    
    if sucesso:
        # O retorno que faltava para resolver o erro do Flask:
        return jsonify({"status": "sucesso"}), 200
    else:
        return jsonify({"status": "erro", "mensagem": msg}), 500
    
def receive_frame(img_width,img_height,img_data):
    global latest_frame, status_cam
    try:
        # Converte o buffer para array numpy e redimensiona
        frame = np.frombuffer(img_data, dtype=np.uint8).reshape((img_height, img_width, 3))

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        latest_frame = frame
        
        # O NAO geralmente envia em RGB, mas o OpenCV/Navegador costuma esperar BGR ou vice-versa
        # Se as cores ficarem estranhas, usar: frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        print("Sucesso na conversao da imagem")
        return True, "Sucesso"
    
    except Exception as e:
        print(f"Erro ao processar frame: {e}")
        return False, str(e)

def gen_frames():
    global latest_frame, status_cam
    while status_cam:
        if latest_frame is not None:
            # Codifica para JPG para diminuir o peso do streaming
            ret, buffer = cv2.imencode('.jpg', latest_frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            print("Sucesso ao gerar imagem jpeg")
        
        # Pequena pausa para não estressar a CPU se não houver frames novos
        time.sleep(0.03) 

@app.route('/get_latest_frame', methods=['GET'])
def get_latest_frame():
    global latest_frame

    if latest_frame is None:
        return jsonify({"status": "erro", "mensagem": "Nenhum frame disponivel"}), 404
    
    ret, buffer = cv2.imencode('.jpg', latest_frame)
    if not ret:
        return jsonify({"status": "erro", "mensagem": "Falha ao codificar"}), 500
        
    return Response(buffer.tobytes(), mimetype='image/jpeg')

@app.route('/video')
def video():
    # Retorna o streaming usando multipart/x-mixed-replace
    print("Sucesso ao enviar imagem para o navegador")
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)