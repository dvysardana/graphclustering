__author__ = 'divya'

from MKNN_Helper import MKNN_Helper

import pylab as pl
import numpy as np

class MKNN_Helper_Plot(MKNN_Helper):
    def __init__(self, out_filename, phase):
        super(MKNN_Helper_Plot, self).__init__()
        self.out_filename = out_filename

    # def plot_evaluation_data(self):
    #     self.configdata.logger.debug("Debugging from inside method plot_evaluation_data of class MKNN_Helper_Plot.")
    #     figurename1 = self.configdata.eval_results_dir + "/plots/phase" + str(self.phase) + "/" + self.configdata.currentdate_str + "_Clusterone_" + self.configdata.dataset_name + "_meandiff_All" + "_Phase_" + str(self.phase) + "_plot_1.png"
    #
    #     fig = pl.figure()
    #     ax = fig.add_subplot(111)
    #     ax.plot(mean_diff_list, num_clusters_size_2_or_more_list, 'g', label='Total no. of clusters (size >=2)')
    #
    #     # Shrink current axis's height by 10% on the bottom
    #     box = ax.get_position()
    #     ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.7])
    #
    #     # Put a legend below current axis
    #     lgd = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=5, fontsize=12)
    #     #ax.legend()
    #
    #     ax.set_title('Number of Clusters vs. K', fontsize=14)
    #     ax.set_xlabel('K', fontsize=12)
    #     ax.set_ylabel('Number of Clusters', fontsize=12)
    #     ax.set_yticks(np.arange(min(num_clusters_size_3_or_more_list), max(num_clusters_size_3_or_more_list)+2))
    #
    #
    #     fig.savefig(figurename1, dpi=300, format='png', bbox_extra_artists=(lgd,), bbox_inches='tight')
    #     pl.close("all")
