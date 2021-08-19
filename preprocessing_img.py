from skimage import io 
import threading
import os
def clear_folder(folder_name):
    a=os.listdir(folder_name)
    for file_ in a:
        os.remove(os.path.join(folder_name,file_))
    print(str(len(a))+" files in '"+folder_name+"' folder deleted")
mutex = threading.Lock()
class Im_preprocess:
    correct_idx=[] #index in urls that have been downloaded normally
    img_list=[]
    def from_urls_to_array(self,urls):
        threads=[]
        for i in range(len(urls)):
            t=threading.Thread(target=self.load_one_image,args=[urls,i])
            t.start()
            threads.append(t)
            
        for thread in threads:
            thread.join()
    
    def load_one_image(self,urls,i):
        try:
            img=io.imread(urls[i])#load concurrently
            
            mutex.acquire() #mutex lock
            self.img_list.append(img)
            self.correct_idx.append(i)
            mutex.release() #mutex release
        except:
            pass
    
    def write_img(self, path):
        for i in range(len(self.img_list)):
            io.imsave( path+format(i,'04d')+".png",self.img_list[i])
    def close(self):
        self.correct_idx=[]
        self.img_list=[]
