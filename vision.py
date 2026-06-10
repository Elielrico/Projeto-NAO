from flask import Flask, request, Response, jsonify
import numpy as np
import cv2
import base64
import time

app = Flask(__name__)

# Variável global para armazenar o último frame recebido
latest_frame = None
status_cam = None

@app.route('/frame', methods=['POST'])
def receive_frame():
    global latest_frame, status_cam
    try:
        data = request.json
        width = data['width']
        height = data['height']
        img_data = base64.b64decode(data['image'])
        status_cam = data['status']

        # Converte o buffer para array numpy e redimensiona
        frame = np.frombuffer(img_data, dtype=np.uint8).reshape((height, width, 3))

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # O NAO geralmente envia em RGB, mas o OpenCV/Navegador costuma esperar BGR ou vice-versa
        # Se as cores ficarem estranhas, use: frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        latest_frame = frame
        print("Sucesso na conversao da imagem")
        print(f"Status da camera: {status_cam}")
        return jsonify(status="success")
    
    except Exception as e:
        print(f"Erro ao processar frame: {e}")
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

def gen_frames():
    global latest_frame
    while True:
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

@app.route('/video')
def video():
    # Retorna o streaming usando multipart/x-mixed-replace
    print("Sucesso ao enviar imagem para o navegador")
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)