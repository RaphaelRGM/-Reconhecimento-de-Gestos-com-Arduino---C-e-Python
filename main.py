import cv2
import mediapipe as mp
import serial
import time
import json

# Configurar a porta serial (ajuste para a porta correta do seu Arduino)
arduino = serial.Serial('COM4', 9600, timeout=1)
time.sleep(2)  # Aguarda a inicialização da conexão serial

# Inicializa o MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()  # Parâmetros padrão de detecção e tracking
mp_draw = mp.solutions.drawing_utils

def count_fingers(hand_landmarks):
    """
    Conta os dedos levantados (exceto o polegar) comparando a posição do dedo (tip)
    com a posição do respectivo PIP (primeira junta) para cada dedo.
    """
    count = 0

    # Índice: tip = landmark[8], PIP = landmark[6]
    if hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y:
        count += 1
    # Médio: tip = landmark[12], PIP = landmark[10]
    if hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y:
        count += 1
    # Anelar: tip = landmark[16], PIP = landmark[14]
    if hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y:
        count += 1
    # Mínimo: tip = landmark[20], PIP = landmark[18]
    if hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y:
        count += 1

    return count

# Abra um vídeo (pode ser de um arquivo ou da webcam; use 0 para webcam)
video_path = "video.mp4"  # Substitua pelo caminho do seu vídeo ou use 0 para a câmera
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Fim do vídeo ou erro ao carregar.")
        break

    # Redimensiona para 500x500 para facilitar a visualização
    frame = cv2.resize(frame, (500, 500))
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            finger_count = count_fingers(hand_landmarks)
            cv2.putText(frame, f"Fingers: {finger_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
            # Prepara o pacote JSON conforme o valor detectado:
            # Envia {"valor": 1} se 1 dedo for detectado,
            # {"valor": 2} se 2 dedos forem detectados,
            # ou {"valor": 0} se outro número for detectado.
            if finger_count == 1:
                data = {"valor": 1}
            elif finger_count == 2:
                data = {"valor": 2}
            else:
                data = {"valor": 0}
            
            pacote = json.dumps(data) + "\n"  # Adiciona '\n' para facilitar a leitura no Arduino
            arduino.write(pacote.encode('utf-8'))
            print("Enviado:", pacote.strip())

    cv2.imshow("Video", frame)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
