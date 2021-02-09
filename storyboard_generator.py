#
#   Don't use it, I'm bad at this.
#

import cv2
import json

videoFile = "example.mp4" # specify your video file name
osbFile = "output.osb" # specify your file name

resizeWidth = 160 # higher = more elements = increased filesize
resizeHeight = 120 # higher = more elements = increased filesize

squareWidth = (640 / resizeWidth)
squareHeight = (480 / resizeHeight)

frameCount = 1 # don't touch it
allFrames = 0 # don't touch it

baseFPS = 0 # framerate of video
FPS = 10 # change this value to storyboard framerate

def calculateTime(i):
    return int(((i * (baseFPS/FPS)) / baseFPS) * 1000) # this is retarded

def convertToFrames():
    global allFrames, frameCount, baseFPS

    cap = cv2.VideoCapture(videoFile)

    allFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    baseFPS = cap.get(cv2.CAP_PROP_FPS)

    while(cap.isOpened()):
        ret, frame = cap.read()

        if ret == False:
            break

        frame = cv2.resize(frame,(resizeWidth,resizeHeight),fx=0,fy=0, interpolation = cv2.INTER_CUBIC) # resize frame by frame

        height, width, channels = frame.shape

        tmp = {}

        for x in range(0, width):
            for y in range(0, height):
                color = float(frame[y,x,0]) * float(frame[y,x,0]) * float(frame[y,x,0])

                if color >= 8290687.5: #(255*255*255)/2
                    color = 1 # white
                else:
                    color = 0 # black

                try:
                    tmp[x][y] = color
                except KeyError:
                    tmp[x] = {}
                    tmp[x][y] = color

        frameData = open("frames/frame_{0}.json".format(frameCount), "w")
        frameData.write(json.dumps(tmp))
        frameData.close()
        
        print("Frame: {0}/{1}".format(frameCount, allFrames))

        frameCount += 1

def generateStoryboard():
    allFrames = int(frameCount*(FPS/baseFPS)) # float to int (pretty good)
    allFramesData = []

    osbEditor = open(osbFile, "a+")
    osbEditor.write("[Events]\n")

    for frame in range(1, allFrames):
        currentFrameNumber = int(frame * (baseFPS/FPS))

        tmp = open("frames/frame_{0}.json".format(currentFrameNumber), "r")
        allFramesData.append(json.loads(tmp.read()))
        tmp.close()

    for x in range(1, resizeWidth):
        for y in range(1, resizeHeight):
            lastTime = 0
            pos = [squareWidth * (x - 1), squareHeight * (y-1)]
            osbEditor.write("Sprite,Background,TopLeft,\"white.png\",{0},{1}\n".format(int(pos[0]),int(pos[1])))

            for frame in range(0,len(allFramesData)):
                if int(allFramesData[frame][str(x)][str(y)]) == 1:
                    osbEditor.write("_F,0,{0},{1},0\n".format(lastTime, calculateTime(frame)))
                    osbEditor.write("_F,0,{0},{1},1\n".format(calculateTime(frame), calculateTime(frame+1)))
                    lastTime = calculateTime(frame+1)

            print("Created Pixel: {0}x{1}".format(x, y))

    osbEditor.write("""//Storyboard Layer 1 (Fail)
//Storyboard Layer 2 (Pass)
//Storyboard Layer 3 (Foreground)
//Storyboard Layer 4 (Overlay)
//Storyboard Sound Samples""")
    osbEditor.close()

def main():
    print("Storyboard Converter")
    print("Starting converting frames to data.")
    convertToFrames()

    print("Done.")
    print("Starting converting data to storyboard.")
    generateStoryboard()

    print("Done.")
    print("create a white.png file in beatmap directory with white background and dimensions ({0}px x {1}px)".format(squareWidth, squareHeight))

main()