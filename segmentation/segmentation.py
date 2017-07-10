# coding: utf-8

"""
@author: Philippenko
This class is devoted to the segmentation of a time serie.
There is also the associated tools for the printing of the segmentation elements.
"""

import matplotlib.pyplot as plt
from statistics import median

import segmentation_construction as com
import manual as man
from storage import save as sv
from dba import DBA
    
class Segmentation:
    
    def __init__(self, **keys):
        if 'segments' in keys: self.loading(**keys)
        else: self.initialisation(**keys)
    
    def initialisation(self, serie,order, activity, automatic=True, compute=True, absc=[]):
        self.serie=serie
        self.order=[]
        self.activity=activity
        self.absc=absc
        if automatic:
            self.sd_serie=com.preparation(serie,order)
            self.breaking_points=com.selection_relevant_points(com.compute_breaking_points(serie, self.sd_serie))
        else:
            print("Manuel segmentation")
            self.sd_serie=[]
            if absc==[]:
                self.breaking_points=man.manuel_selection_breaking_points(self.serie)[1:]
            else:
                self.breaking_points=man.manuel_selection_breaking_points_with_time(self.absc, self.serie)
            # The first breaking point mark the beginning of the movement.
            # While the last breaking point mark the end of all mouvements.
            # In this manner, one performs an index shift so as to keep only the significant points.
            print(self.breaking_points)
            self.serie=self.serie[self.breaking_points[0]:self.breaking_points[len(self.breaking_points)-1]]
            self.breaking_points=[b-self.breaking_points[0] for b in self.breaking_points]
        # If there is a duplicate points, the variance segmentation_construction will fail.
        # This case is possible with the manually method.
        self.breaking_points=sorted(list(set(self.breaking_points)))
        self.segments=com.compute_segments(self.breaking_points, serie)
        self.segments=[com.normalization(s) for s in self.segments]
        if compute==True:
            print("Computing the average segment via DBA ...")
            (self.average_segment,self.dispersion_segment)=DBA(self.segments,3)
        else:
            self.average_segment=[]
            self.dispersion_segment=[]
            
    def loading(self,absc,serie,order,activity,sd_serie,breaking_points,segments,average_segment,dispersion_segment):
        self.serie=serie
        self.order=order
        self.absc=[]
        self.activity=activity
        self.sd_serie=sd_serie
        self.breaking_points=breaking_points
        self.segments=segments
        self.average_segment=average_segment
        self.dispersion_segment=dispersion_segment   
        
    def get_absc(self):
        return self.absc
        
    def get_serie(self):
        return self.serie
    
    def get_order(self):
        return self.order
    
    def get_activity(self):
        return self.activity
    
    def get_sd_serie(self):
        return self.sd_serie
    
    def get_breaking_points(self):
        return self.breaking_points
    
    def get_segments(self):
        return self.segments
    
    def get_average_segment(self):
        return self.average_segment
    
    def get_dispersion_segment(self):
        return self.dispersion_segment
    
    def get_all(self):
        return(self.absc, self.serie,self.order,self.sd_serie,self.sd_serie,self.breaking_points,
               self.segments, self.average_segment, self.dispersion_segment)
        
    def recompute_average_segment(self, iteration):
        self.segments=com.compute_segments(self.breaking_points, self.serie)
        self.segments=[com.normalization(s) for s in self.segments]
        (self.average_segment,self.dispersion_segment)=DBA(self.segments,iteration)
        
    def prunning_breaking_points(self):
        self.breaking_points=sorted(list(set(self.breaking_points)))
        
    def recompute_bp(self):
        self.breaking_points=sorted(list(set(self.breaking_points)))
        
    def recompute_segments(self):
        self.recompute_bp()
        self.segments=com.compute_segments(self.breaking_points, self.serie)
        self.segments=[com.normalization(s) for s in self.segments]
        
        
    def store(self,filepath):
        sv.save_list(self.absc, filepath+"\\time.csv")
        sv.save_list(self.serie, filepath+"\\serie.csv")
        sv.save_list(self.breaking_points, filepath+"\\breaking_points.csv")
        sv.save_segments(self.segments, filepath+"\\segments.txt")
        sv.save_list(self.average_segment,filepath+"\\average_segment.csv")
        sv.save_list(self.dispersion_segment,filepath+"\\dispersion_segment.csv")    
    
    # Affichage de la superposition des segments.
    def plot_segments_superposition(self, filepath,save=True):
        plt.figure(figsize=(15, 4))
        for  s in self.segments:
            plt.plot(s)
        plt.title("Segments")
        save_or_not(save, filepath+"\\segments_superposition.png")
        
    def plot_serie(self, filepath,save=True):
        plt.figure(figsize=(15, 4))
        plt.plot(self.serie)  
        plt.title(self.activity)
        save_or_not(save, filepath+"\\serie.png")
        
    def plot_breaking_points(self, filepath,save=True):
        plt.figure(figsize=(15, 4))
        plt.plot(self.serie)  
        plt.title(self.activity)
        # Affichage d'une barre verticale � chaque point de rupture
        for p in self.breaking_points:
            plt.axvline(x=p, linewidth=0.5, color='r')
        save_or_not(save,filepath+"\\breaking_points.png")
        
    def plot_smooth_diff(self, filepath,save=True):
        plt.figure(figsize=(15, 4))
        plt.plot(self.sd_serie)  
        plt.title("Smoothing and Differenciation")  
        plt.savefig(filepath+"\\smooth_diff.png")
        
    def plot_average_segment(self, filepath,save=True):
        plt.figure(figsize=(2, 4))
        plt.plot(self.average_segment)
        plt.plot([self.average_segment[i]-3*self.dispersion_segment[i] for i in range(len(self.average_segment))],'--r')
        plt.plot([self.average_segment[i]+3*self.dispersion_segment[i] for i in range(len(self.average_segment))],'--r')
        plt.title("Average_segment")       
        save_or_not(save,filepath+"\\average_segment.png") 
    
    def display_segmentation(self,filepath,save=True):
        self.plot_breaking_points(filepath)
        self.plot_segments_superposition(filepath)
        self.plot_average_segment(filepath)
        
    def check_break_points_index_increasing(self):
        prev=0
        for p in self.breaking_points:
            if prev>p:
                print("There is a problem with the couple ", (prev,p))
            prev=p
            
    def aberant_points(self):
        distance=[self.breaking_points[i]-self.breaking_points[i-1] for i in range(1,len(self.breaking_points))]
        med=median(distance)
        for i in range(len(distance)):
            if not com.little_variation(med, distance[i], 50):
                print("The distance is too big !")
                print("Distance : ", distance[i])
                print("Point :", i)
        
def save_or_not(save,filepath):
    if save:
        plt.savefig(filepath)
        plt.close()
    else: 
        plt.show()


