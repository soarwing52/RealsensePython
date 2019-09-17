import cv2

img_file = r'C:\Users\cyh\Documents\GitHub\RealsensePython\examples/google earth.PNG'
img = cv2.imread(img_file)


# Adding Function Attached To Mouse Callback
def draw(event,x,y,flags,params):
    global ix,iy,drawing
    print event, x, y ,flags, params
    img_file = 'examples/google earth.PNG'
    img = cv2.imread(img_file)

    # Left Mouse Button Down Pressed
    if(event==1):

        drawing = True
        ix = x
        iy = y

    if(flags==1):
        if(drawing==True):
            #For Drawing Line
            cv2.line(img,pt1=(ix,iy),pt2=(x,y),color=(255,255,255),thickness=3)
            cv2.imshow("Window", img)
            #ix = x
            #iy = y
            # For Drawing Rectangle
            # cv2.rectangle(image,pt1=(ix,iy),pt2=(x,y),color=(255,255,255),thickness=3)

    if(event==4):
        #cv2.line(img, pt1=(ix, iy), pt2=(x, y), color=(255, 255, 255), thickness=3)
        drawing = False
        #cv2.imshow("Window", img)



# Making Window For The Image
cv2.namedWindow("Window")

# Adding Mouse CallBack Event
cv2.setMouseCallback("Window",draw)
cv2.imshow("Window",img)
# Starting The Loop So Image Can Be Shown
while(True):
    key = cv2.waitKey(1000)
    if key & 0xFF == ord('q'):
        break
    elif key == 32:
        img = cv2.imread(img_file)
        cv2.imshow("Window", img)

cv2.destroyAllWindows()