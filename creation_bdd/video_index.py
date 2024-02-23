import sys 
import os 

def add_video_index(base_path):
    for video_path in os.listdir(base_path):
        video_index = str(video_path)
        for frame in os.listdir(os.path.join(base_path, video_path)):
            frame_path = os.path.join(base_path, video_path, frame)
            base, midle, end = frame.split('_')
            # print("old path: ",frame_path)
            # print("new path: ",os.path.join(base_path, video_path, base + '_' + video_index + '_' + midle + '_' + end))
            old_path = os.path.join(frame_path)
            new_path = os.path.join(base_path, video_path, base + '_' + video_index + '_' + midle + '_' + end)
            os.rename(old_path, new_path)
            print("Renamed: ", old_path, " to: ", new_path)




if len(sys.argv) != 2:
    print("Usage: python video_index.py <base_path>")
    sys.exit(1)

base_path = sys.argv[1] # base path is the path to the folder containting the video folders

add_video_index(base_path)