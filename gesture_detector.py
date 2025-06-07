import cv2
import mediapipe as mp
import time
from supabase_client import send_alerts
from utils import get_timestamp, get_latlon_from_endereco
import os
from PIL import Image
import numpy as np

def draw_text_with_background(img, text, pos, font, scale, color, thickness, bg_color, alpha=0.5, border_radius=0):
    (w, h), baseline = cv2.getTextSize(text, font, scale, thickness)
    x, y = pos
    x1, y1 = x - 5, y - h - 5
    x2, y2 = x + w + 5, y + baseline + 5

    overlay = img.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), bg_color, -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    cv2.putText(img, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)

def overlay_logo_centered(frame, logo_img, bar_height):
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, 0), (w, bar_height), (255, 255, 255), -1)
    logo_h, logo_w = logo_img.shape[:2]
    total_width = logo_w + 10 + 90
    logo_x = w // 2 - total_width // 2
    logo_y = bar_height // 2 - logo_h // 2
    if logo_img.shape[-1] == 4:
        logo_bgr = logo_img[..., :3]
        mask = logo_img[..., 3:] / 255.0
    else:
        logo_bgr = logo_img
        mask = np.ones((logo_h, logo_w, 1))
    roi = frame[logo_y:logo_y+logo_h, logo_x:logo_x+logo_w]
    frame[logo_y:logo_y+logo_h, logo_x:logo_x+logo_w] = (roi * (1 - mask) + logo_bgr * mask).astype(np.uint8)
    text = "Alertae"
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.8
    thickness = 2
    (text_w, text_h), _ = cv2.getTextSize(text, font, scale, thickness)
    text_x = logo_x + logo_w + 10
    text_y = bar_height // 2 + text_h // 2 - 2
    cv2.putText(frame, text, (text_x, text_y), font, scale, (0, 0, 0), thickness, cv2.LINE_AA)

def detectar_gesto(nome, emails, cep, endereco_completo):
    lat, lon = get_latlon_from_endereco(endereco_completo)
    print(f"Localização aproximada para alerta: {lat}, {lon}")

    mp_hands = mp.solutions.hands
    mp_pose = mp.solutions.pose
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
    pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    cap = cv2.VideoCapture(0)

    logo_img = None
    if os.path.exists("logo.png"):
        pil_logo = Image.open("logo.png").convert("RGBA").resize((60, 60))
        logo_img = np.array(pil_logo)

    cooldown_segundos_moderado = 30
    cooldown_segundos_severo = 60
    ultimo_alerta_moderado = 0
    ultimo_alerta_severo = 0
    tempo_exibir_moderado = 0
    tempo_exibir_severo = 0

    estados_moderado = []
    tempos_moderado = []

    status_moderado_restante = 0
    status_severo_restante = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        frame = cv2.flip(frame, 1)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result_hands = hands.process(img_rgb)
        result_pose = pose.process(img_rgb)
        alerta_atual_frame = "Nenhum"

        # --- DRAW HAND LANDMARKS (linhas brancas, bolinhas azuis discretas) ---
        if result_hands.multi_hand_landmarks:
            for hand_landmarks in result_hands.multi_hand_landmarks:
                points = [(int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])) for lm in hand_landmarks.landmark]
                for i, j in mp_hands.HAND_CONNECTIONS:
                    xi, yi = points[i]
                    xj, yj = points[j]
                    cv2.line(frame, (xi, yi), (xj, yj), (255, 255, 255), 1, cv2.LINE_AA)
                for cx, cy in points:
                    cv2.circle(frame, (cx, cy), 2, (255, 102, 0), -1)  # bolinhas azul discretas

        # --- DRAW POSE LANDMARKS (sem linhas do olho/boca, bolinhas azuis discretas) ---
        if result_pose.pose_landmarks:
            pose_connections = [
                (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER),
                (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW),
                (mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST),
                (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW),
                (mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST),
                (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP),
                (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_HIP),
                (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP),
                (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE),
                (mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE),
                (mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE),
                (mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE),
            ]
            landmarks = result_pose.pose_landmarks.landmark
            for start, end in pose_connections:
                x1, y1 = int(landmarks[start].x * frame.shape[1]), int(landmarks[start].y * frame.shape[0])
                x2, y2 = int(landmarks[end].x * frame.shape[1]), int(landmarks[end].y * frame.shape[0])
                cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2, cv2.LINE_AA)
            pontos_corpo = [
                mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER,
                mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.RIGHT_ELBOW,
                mp_pose.PoseLandmark.LEFT_WRIST, mp_pose.PoseLandmark.RIGHT_WRIST,
                mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP,
                mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.RIGHT_KNEE,
                mp_pose.PoseLandmark.LEFT_ANKLE, mp_pose.PoseLandmark.RIGHT_ANKLE
            ]
            for idx in pontos_corpo:
                lm = landmarks[idx]
                cx, cy = int(lm.x * frame.shape[1]), int(lm.y * frame.shape[0])
                cv2.circle(frame, (cx, cy), 3, (255, 102, 0), -1)  # bolinhas azul discretas

        # Inicializa os estados e tempos para o número de mãos detectadas
        if result_hands.multi_hand_landmarks:
            num_maos = len(result_hands.multi_hand_landmarks)
            while len(estados_moderado) < num_maos:
                estados_moderado.append(0)
            while len(tempos_moderado) < num_maos:
                tempos_moderado.append(time.time())
        else:
            estados_moderado = []
            tempos_moderado = []

        # --- ALERTA MODERADO ---
        if result_hands.multi_hand_landmarks:
            for idx, (hand_landmarks, handedness) in enumerate(zip(result_hands.multi_hand_landmarks, result_hands.multi_handedness)):
                pontos = hand_landmarks.landmark
                hand_label = handedness.classification[0].label
                dedos_estendidos = []
                for dedo_tip_id in [mp_hands.HandLandmark.INDEX_FINGER_TIP,
                                    mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                                    mp_hands.HandLandmark.RING_FINGER_TIP,
                                    mp_hands.HandLandmark.PINKY_TIP]:
                    dedos_estendidos.append(pontos[dedo_tip_id].y < pontos[dedo_tip_id - 2].y)
                mao_aberta = all(dedos_estendidos)
                if hand_label == "Right":
                    polegar_dobrado = pontos[mp_hands.HandLandmark.THUMB_TIP].x > pontos[mp_hands.HandLandmark.THUMB_IP].x
                else:
                    polegar_dobrado = pontos[mp_hands.HandLandmark.THUMB_TIP].x < pontos[mp_hands.HandLandmark.THUMB_IP].x
                punho_fechado = True
                for dedo_tip_id in [mp_hands.HandLandmark.INDEX_FINGER_TIP,
                                    mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                                    mp_hands.HandLandmark.RING_FINGER_TIP,
                                    mp_hands.HandLandmark.PINKY_TIP]:
                    if pontos[dedo_tip_id].y < pontos[dedo_tip_id - 3].y:
                        punho_fechado = False
                        break
                punho_fechado = punho_fechado and abs(pontos[mp_hands.HandLandmark.THUMB_TIP].y - pontos[mp_hands.HandLandmark.INDEX_FINGER_MCP].y) < 0.15
                if mao_aberta and not polegar_dobrado:
                    estados_moderado[idx] = 0
                    tempos_moderado[idx] = time.time()
                elif mao_aberta and polegar_dobrado and estados_moderado[idx] == 0:
                    estados_moderado[idx] = 1
                    tempos_moderado[idx] = time.time()
                elif punho_fechado and estados_moderado[idx] == 1 and (time.time() - tempos_moderado[idx] < 3):
                    estados_moderado[idx] = 2
                    tempo_atual = time.time()
                    status_moderado_restante = max(0, int(cooldown_segundos_moderado - (tempo_atual - ultimo_alerta_moderado)))
                    if tempo_atual - ultimo_alerta_moderado > cooldown_segundos_moderado:
                        timestamp = get_timestamp()
                        message = f"ALERTA MODERADO: {nome} pediu ajuda (Sinal Universal) às {timestamp} na região do CEP {cep}."
                        send_alerts(nome, emails, message, lat, lon)
                        ultimo_alerta_moderado = tempo_atual
                        alerta_atual_frame = "MODERADO"
                        print("✅ Alerta Moderado enviado!")
                        status_moderado_restante = cooldown_segundos_moderado
                        tempo_exibir_moderado = tempo_atual + 4
                    else:
                        alerta_atual_frame = "MODERADO (Aguardando)"

        # --- ALERTA SEVERO ---
        if result_hands.multi_hand_landmarks and len(result_hands.multi_hand_landmarks) == 2 and result_pose.pose_landmarks:
            pose_landmarks = result_pose.pose_landmarks.landmark
            left_shoulder = pose_landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = pose_landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            shoulder_y_avg = (left_shoulder.y + right_shoulder.y) / 2

            wrists = []
            maos_abertas_count = 0

            for hand_landmarks, handedness in zip(result_hands.multi_hand_landmarks, result_hands.multi_handedness):
                pontos = hand_landmarks.landmark
                wrist = pontos[mp_hands.HandLandmark.WRIST]
                wrists.append((wrist.x, wrist.y))
                dedos_estendidos = []
                for dedo_tip_id in [mp_hands.HandLandmark.INDEX_FINGER_TIP,
                                    mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                                    mp_hands.HandLandmark.RING_FINGER_TIP,
                                    mp_hands.HandLandmark.PINKY_TIP]:
                    dedos_estendidos.append(pontos[dedo_tip_id].y < pontos[dedo_tip_id - 2].y)
                if all(dedos_estendidos):
                    maos_abertas_count += 1

            if maos_abertas_count == 2:
                x1, y1 = wrists[0]
                x2, y2 = wrists[1]
                distancia_maos = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
                # Checa se os pulsos estão NA ALTURA OU ABAIXO dos ombros
                if y1 >= shoulder_y_avg and y2 >= shoulder_y_avg:
                    if distancia_maos < 0.15:
                        tempo_atual = time.time()
                        status_severo_restante = max(0, int(cooldown_segundos_severo - (tempo_atual - ultimo_alerta_severo)))
                        if tempo_atual - ultimo_alerta_severo > cooldown_segundos_severo:
                            timestamp = get_timestamp()
                            message = f"🚨 ALERTA SEVERO: {nome} pediu ajuda (Gestos com dois braços cruzados) às {timestamp} na região do CEP {cep}."
                            send_alerts(nome, emails, message, lat, lon)
                            ultimo_alerta_severo = tempo_atual
                            alerta_atual_frame = "SEVERO"
                            print("🚨 Alerta Severo enviado!")
                            status_severo_restante = cooldown_segundos_severo
                            tempo_exibir_severo = tempo_atual + 4
                        else:
                            alerta_atual_frame = "SEVERO (Aguardando)"

        # --- BARRA SUPERIOR COM LOGO E NOME ---
        bar_height = 70
        if logo_img is not None:
            overlay_logo_centered(frame, logo_img, bar_height)
        else:
            h, w = frame.shape[:2]
            cv2.rectangle(frame, (0, 0), (w, bar_height), (255, 255, 255), -1)
            text = "Alertae"
            font = cv2.FONT_HERSHEY_SIMPLEX
            scale = 0.8
            thickness = 2
            (text_w, text_h), _ = cv2.getTextSize(text, font, scale, thickness)
            text_x = w // 2 - text_w // 2
            text_y = bar_height // 2 + text_h // 2 - 2
            cv2.putText(frame, text, (text_x, text_y), font, scale, (0, 0, 0), thickness, cv2.LINE_AA)

        # --- INFORMAÇÕES DE STATUS NO TOPO ESQUERDA ---
        bg_cor_status = (240, 240, 240)
        agora = time.time()
        status_y_start = bar_height + 15
        status_x = 20
        status_font = cv2.FONT_HERSHEY_SIMPLEX
        status_scale = 0.6
        status_thickness = 1

        if status_moderado_restante > 0:
            draw_text_with_background(
                frame,
                f"Status Moderado: {status_moderado_restante}s",
                (status_x, status_y_start),
                status_font,
                status_scale,
                (0, 0, 0),
                status_thickness,
                bg_cor_status,
                alpha=0.7,
                border_radius=5
            )

        if status_severo_restante > 0:
            draw_text_with_background(
                frame,
                f"Status Severo: {status_severo_restante}s",
                (status_x, status_y_start + 30),
                status_font,
                status_scale,
                (0, 0, 0),
                status_thickness,
                bg_cor_status,
                alpha=0.7,
                border_radius=5
            )

        # --- TIPOS DE ALERTA EMBAIXO DA TELA ---
        bottom_margin = 30
        alert_text_y = frame.shape[0] - bottom_margin
        alert_font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        alert_scale = 1.2
        alert_thickness = 2
        alert_bg_alpha = 0.8
        alert_border_radius = 10

        current_display_alert = "Nenhum Alerta Detectado"
        alert_color = (0, 0, 0)
        alert_bg_color = (180, 255, 180)

        if alerta_atual_frame.startswith("SEVERO") or (tempo_exibir_severo > agora):
            current_display_alert = "ALERTA SEVERO ATIVO!"
            alert_bg_color = (180, 180, 255)
            if alerta_atual_frame == "SEVERO":
                tempo_exibir_severo = agora + 4
        elif alerta_atual_frame.startswith("MODERADO") or (tempo_exibir_moderado > agora):
            current_display_alert = "ALERTA MODERADO ATIVO!"
            alert_bg_color = (180, 255, 255)
            if alerta_atual_frame == "MODERADO":
                tempo_exibir_moderado = agora + 4

        (alert_w, alert_h), _ = cv2.getTextSize(current_display_alert, alert_font, alert_scale, alert_thickness)
        alert_text_x = (frame.shape[1] - alert_w) // 2

        draw_text_with_background(
            frame,
            current_display_alert,
            (alert_text_x, alert_text_y),
            alert_font,
            alert_scale,
            alert_color,
            alert_thickness,
            alert_bg_color,
            alpha=alert_bg_alpha,
            border_radius=alert_border_radius
        )

        cv2.imshow("Detecção de Gestos de Emergência", frame)

        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()