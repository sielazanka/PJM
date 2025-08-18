import json
import cv2
import os


def detect_motion(video_path, threshold=25, min_area=500):
    cap = cv2.VideoCapture(video_path)
    motion_flags = []

    # Read the first frame
    ret, prev_frame = cap.read()
    if not ret:
        print(f"Nie można otworzyć pliku: {video_path}")
        return []

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

    # motion_flags.append(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Frame difference
        frame_delta = cv2.absdiff(prev_gray, gray)
        thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Find contours (moving regions)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = 0
        for contour in contours:
            if cv2.contourArea(contour) >= min_area:
                motion_detected = 1
                break

        motion_flags.append(motion_detected)

        prev_gray = gray

    cap.release()
    return motion_flags


def display_motion_only(video_path, motion_flags):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Nie można otworzyć pliku: {video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or len(motion_flags)

    if len(motion_flags) < total_frames:
        motion_flags = motion_flags + [0] * (total_frames - len(motion_flags))
    elif len(motion_flags) > total_frames:
        motion_flags = motion_flags[:total_frames]

    motion_indices = [i for i, f in enumerate(motion_flags) if f == 1]

    if not motion_indices:
        print("Nie wykryto ruchu.")
        cap.release()
        return

    def read_frame_at(idx):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        return frame if ok else None

    for idx in motion_indices:
        frame = read_frame_at(idx)
        if frame is None:
            continue

        cv2.imshow("PJM", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cap.release()


# Wczytaj mapping
with open('mapping.json', 'r', encoding='utf-8') as f:
    mapping = json.load(f)

# Pobierz tekst od użytkownika
text = input("Wpisz zdanie do przetłumaczenia na PJM: ")
tokens = text.lower().split()

# Utwórz sekwencję klipów
clips = []
for token in tokens:
    clip_file = mapping.get(token)
    if clip_file:
        clips.append(os.path.join('pjm_clips', clip_file))
    else:
        print(f"Brak klipu dla słowa: {token}")

# Odtwarzaj po kolei klipy
for clip_path in clips:
    cap = cv2.VideoCapture(clip_path)
    motion_clips = detect_motion(clip_path)
    if not cap.isOpened():
        print(f"Nie można otworzyć pliku: {clip_path}")
        continue
    display_motion_only(clip_path, motion_clips)
cv2.destroyAllWindows()
