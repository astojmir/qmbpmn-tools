#
# ===========================================================================
#
#                            PUBLIC DOMAIN NOTICE
#               National Center for Biotechnology Information
#
#  This software/database is a "United States Government Work" under the
#  terms of the United States Copyright Act.  It was written as part of
#  the author's official duties as a United States Government employee and
#  thus cannot be copyrighted.  This software/database is freely available
#  to the public for use. The National Library of Medicine and the U.S.
#  Government have not placed any restriction on its use or reproduction.
#
#  Although all reasonable efforts have been taken to ensure the accuracy
#  and reliability of the software and data, the NLM and the U.S.
#  Government do not and cannot warrant the performance or results that
#  may be obtained by using this software or data. The NLM and the U.S.
#  Government disclaim all warranties, express or implied, including
#  warranties of performance, merchantability or fitness for any particular
#  purpose.
#
#  Please cite the author in any work or product based on this material.
#
# ===========================================================================
#
# Code author:  Aleksandar Stojmirovic
#
#
# Color schemes were taken from the www.ColorBrewer.org site by Cynthia
# A. Brewer, Geography, Pennsylvania State University.
#
#



__all__ = ['BrewerColors']

# Brewer color schemes
# NEED to put attribution here

def parse_ColorBrewer_CSV(filename):
    with open(filename, 'r') as fp:
        colormap = {}
        keys = []
        for line in fp:
            fields = line.split(',')
            if len(fields[0]):
                key = fields[0] + fields[1]
                colormap[key] = []
                keys.append(key)

            colormap[key].append(tuple(map(int, fields[6:9])))

    return keys, colormap

def print_ColorBrewer_dict(fp, colormap, keys=None):
    if keys == None: keys = colormap.keys()

    fp.write('BrewerColors = {\n')
    for key in keys:
        colors = colormap[key]
        fp.write("                 '%s': %s,\n" % (key, colors.__str__()))
    fp.write('               }\n')


BrewerColors = {
                 'YlGn3': [(247, 252, 185), (173, 221, 142), (49, 163, 84)],
                 'YlGn4': [(255, 255, 204), (194, 230, 153), (120, 198, 121), (35, 132, 67)],
                 'YlGn5': [(255, 255, 204), (194, 230, 153), (120, 198, 121), (49, 163, 84), (0, 104, 55)],
                 'YlGn6': [(255, 255, 204), (217, 240, 163), (173, 221, 142), (120, 198, 121), (49, 163, 84), (0, 104, 55)],
                 'YlGn7': [(255, 255, 204), (217, 240, 163), (173, 221, 142), (120, 198, 121), (65, 171, 93), (35, 132, 67), (0, 90, 50)],
                 'YlGn8': [(255, 255, 229), (247, 252, 185), (217, 240, 163), (173, 221, 142), (120, 198, 121), (65, 171, 93), (35, 132, 67), (0, 90, 50)],
                 'YlGn9': [(255, 255, 229), (247, 252, 185), (217, 240, 163), (173, 221, 142), (120, 198, 121), (65, 171, 93), (35, 132, 67), (0, 104, 55), (0, 69, 41)],
                 'YlGnBu3': [(237, 248, 177), (127, 205, 187), (44, 127, 184)],
                 'YlGnBu4': [(255, 255, 204), (161, 218, 180), (65, 182, 196), (34, 94, 168)],
                 'YlGnBu5': [(255, 255, 204), (161, 218, 180), (65, 182, 196), (44, 127, 184), (37, 52, 148)],
                 'YlGnBu6': [(255, 255, 204), (199, 233, 180), (127, 205, 187), (65, 182, 196), (44, 127, 184), (37, 52, 148)],
                 'YlGnBu7': [(255, 255, 204), (199, 233, 180), (127, 205, 187), (65, 182, 196), (29, 145, 192), (34, 94, 168), (12, 44, 132)],
                 'YlGnBu8': [(255, 255, 217), (237, 248, 177), (199, 233, 180), (127, 205, 187), (65, 182, 196), (29, 145, 192), (34, 94, 168), (12, 44, 132)],
                 'YlGnBu9': [(255, 255, 217), (237, 248, 177), (199, 233, 180), (127, 205, 187), (65, 182, 196), (29, 145, 192), (34, 94, 168), (37, 52, 148), (8, 29, 88)],
                 'GnBu3': [(224, 243, 219), (168, 221, 181), (67, 162, 202)],
                 'GnBu4': [(240, 249, 232), (186, 228, 188), (123, 204, 196), (43, 140, 190)],
                 'GnBu5': [(240, 249, 232), (186, 228, 188), (123, 204, 196), (67, 162, 202), (8, 104, 172)],
                 'GnBu6': [(240, 249, 232), (204, 235, 197), (168, 221, 181), (123, 204, 196), (67, 162, 202), (8, 104, 172)],
                 'GnBu7': [(240, 249, 232), (204, 235, 197), (168, 221, 181), (123, 204, 196), (78, 179, 211), (43, 140, 190), (8, 88, 158)],
                 'GnBu8': [(247, 252, 240), (224, 243, 219), (204, 235, 197), (168, 221, 181), (123, 204, 196), (78, 179, 211), (43, 140, 190), (8, 88, 158)],
                 'GnBu9': [(247, 252, 240), (224, 243, 219), (204, 235, 197), (168, 221, 181), (123, 204, 196), (78, 179, 211), (43, 140, 190), (8, 104, 172), (8, 64, 129)],
                 'BuGn3': [(229, 245, 249), (153, 216, 201), (44, 162, 95)],
                 'BuGn4': [(237, 248, 251), (178, 226, 226), (102, 194, 164), (35, 139, 69)],
                 'BuGn5': [(237, 248, 251), (178, 226, 226), (102, 194, 164), (44, 162, 95), (0, 109, 44)],
                 'BuGn6': [(237, 248, 251), (204, 236, 230), (153, 216, 201), (102, 194, 164), (44, 162, 95), (0, 109, 44)],
                 'BuGn7': [(237, 248, 251), (204, 236, 230), (153, 216, 201), (102, 194, 164), (65, 174, 118), (35, 139, 69), (0, 88, 36)],
                 'BuGn8': [(247, 252, 253), (229, 245, 249), (204, 236, 230), (153, 216, 201), (102, 194, 164), (65, 174, 118), (35, 139, 69), (0, 88, 36)],
                 'BuGn9': [(247, 252, 253), (229, 245, 249), (204, 236, 230), (153, 216, 201), (102, 194, 164), (65, 174, 118), (35, 139, 69), (0, 109, 44), (0, 68, 27)],
                 'PuBuGn3': [(236, 226, 240), (166, 189, 219), (28, 144, 153)],
                 'PuBuGn4': [(246, 239, 247), (189, 201, 225), (103, 169, 207), (2, 129, 138)],
                 'PuBuGn5': [(246, 239, 247), (189, 201, 225), (103, 169, 207), (28, 144, 153), (1, 108, 89)],
                 'PuBuGn6': [(246, 239, 247), (208, 209, 230), (166, 189, 219), (103, 169, 207), (28, 144, 153), (1, 108, 89)],
                 'PuBuGn7': [(246, 239, 247), (208, 209, 230), (166, 189, 219), (103, 169, 207), (54, 144, 192), (2, 129, 138), (1, 100, 80)],
                 'PuBuGn8': [(255, 247, 251), (236, 226, 240), (208, 209, 230), (166, 189, 219), (103, 169, 207), (54, 144, 192), (2, 129, 138), (1, 100, 80)],
                 'PuBuGn9': [(255, 247, 251), (236, 226, 240), (208, 209, 230), (166, 189, 219), (103, 169, 207), (54, 144, 192), (2, 129, 138), (1, 108, 89), (1, 70, 54)],
                 'PuBu3': [(236, 231, 242), (166, 189, 219), (43, 140, 190)],
                 'PuBu4': [(241, 238, 246), (189, 201, 225), (116, 169, 207), (5, 112, 176)],
                 'PuBu5': [(241, 238, 246), (189, 201, 225), (116, 169, 207), (43, 140, 190), (4, 90, 141)],
                 'PuBu6': [(241, 238, 246), (208, 209, 230), (166, 189, 219), (116, 169, 207), (43, 140, 190), (4, 90, 141)],
                 'PuBu7': [(241, 238, 246), (208, 209, 230), (166, 189, 219), (116, 169, 207), (54, 144, 192), (5, 112, 176), (3, 78, 123)],
                 'PuBu8': [(255, 247, 251), (236, 231, 242), (208, 209, 230), (166, 189, 219), (116, 169, 207), (54, 144, 192), (5, 112, 176), (3, 78, 123)],
                 'PuBu9': [(255, 247, 251), (236, 231, 242), (208, 209, 230), (166, 189, 219), (116, 169, 207), (54, 144, 192), (5, 112, 176), (4, 90, 141), (2, 56, 88)],
                 'BuPu3': [(224, 236, 244), (158, 188, 218), (136, 86, 167)],
                 'BuPu4': [(237, 248, 251), (179, 205, 227), (140, 150, 198), (136, 65, 157)],
                 'BuPu5': [(237, 248, 251), (179, 205, 227), (140, 150, 198), (136, 86, 167), (129, 15, 124)],
                 'BuPu6': [(237, 248, 251), (191, 211, 230), (158, 188, 218), (140, 150, 198), (136, 86, 167), (129, 15, 124)],
                 'BuPu7': [(237, 248, 251), (191, 211, 230), (158, 188, 218), (140, 150, 198), (140, 107, 177), (136, 65, 157), (110, 1, 107)],
                 'BuPu8': [(247, 252, 253), (224, 236, 244), (191, 211, 230), (158, 188, 218), (140, 150, 198), (140, 107, 177), (136, 65, 157), (110, 1, 107)],
                 'BuPu9': [(247, 252, 253), (224, 236, 244), (191, 211, 230), (158, 188, 218), (140, 150, 198), (140, 107, 177), (136, 65, 157), (129, 15, 124), (77, 0, 75)],
                 'RdPu3': [(253, 224, 221), (250, 159, 181), (197, 27, 138)],
                 'RdPu4': [(254, 235, 226), (251, 180, 185), (247, 104, 161), (174, 1, 126)],
                 'RdPu5': [(254, 235, 226), (251, 180, 185), (247, 104, 161), (197, 27, 138), (122, 1, 119)],
                 'RdPu6': [(254, 235, 226), (252, 197, 192), (250, 159, 181), (247, 104, 161), (197, 27, 138), (122, 1, 119)],
                 'RdPu7': [(254, 235, 226), (252, 197, 192), (250, 159, 181), (247, 104, 161), (221, 52, 151), (174, 1, 126), (122, 1, 119)],
                 'RdPu8': [(255, 247, 243), (253, 224, 221), (252, 197, 192), (250, 159, 181), (247, 104, 161), (221, 52, 151), (174, 1, 126), (122, 1, 119)],
                 'RdPu9': [(255, 247, 243), (253, 224, 221), (252, 197, 192), (250, 159, 181), (247, 104, 161), (221, 52, 151), (174, 1, 126), (122, 1, 119), (73, 0, 106)],
                 'PuRd3': [(231, 225, 239), (201, 148, 199), (221, 28, 119)],
                 'PuRd4': [(241, 238, 246), (215, 181, 216), (223, 101, 176), (206, 18, 86)],
                 'PuRd5': [(241, 238, 246), (215, 181, 216), (223, 101, 176), (221, 28, 119), (152, 0, 67)],
                 'PuRd6': [(241, 238, 246), (212, 185, 218), (201, 148, 199), (223, 101, 176), (221, 28, 119), (152, 0, 67)],
                 'PuRd7': [(241, 238, 246), (212, 185, 218), (201, 148, 199), (223, 101, 176), (231, 41, 138), (206, 18, 86), (145, 0, 63)],
                 'PuRd8': [(247, 244, 249), (231, 225, 239), (212, 185, 218), (201, 148, 199), (223, 101, 176), (231, 41, 138), (206, 18, 86), (145, 0, 63)],
                 'PuRd9': [(247, 244, 249), (231, 225, 239), (212, 185, 218), (201, 148, 199), (223, 101, 176), (231, 41, 138), (206, 18, 86), (152, 0, 67), (103, 0, 31)],
                 'OrRd3': [(254, 232, 200), (253, 187, 132), (227, 74, 51)],
                 'OrRd4': [(254, 240, 217), (253, 204, 138), (252, 141, 89), (215, 48, 31)],
                 'OrRd5': [(254, 240, 217), (253, 204, 138), (252, 141, 89), (227, 74, 51), (179, 0, 0)],
                 'OrRd6': [(254, 240, 217), (253, 212, 158), (253, 187, 132), (252, 141, 89), (227, 74, 51), (179, 0, 0)],
                 'OrRd7': [(254, 240, 217), (253, 212, 158), (253, 187, 132), (252, 141, 89), (239, 101, 72), (215, 48, 31), (153, 0, 0)],
                 'OrRd8': [(255, 247, 236), (254, 232, 200), (253, 212, 158), (253, 187, 132), (252, 141, 89), (239, 101, 72), (215, 48, 31), (153, 0, 0)],
                 'OrRd9': [(255, 247, 236), (254, 232, 200), (253, 212, 158), (253, 187, 132), (252, 141, 89), (239, 101, 72), (215, 48, 31), (179, 0, 0), (127, 0, 0)],
                 'YlOrRd3': [(255, 237, 160), (254, 178, 76), (240, 59, 32)],
                 'YlOrRd4': [(255, 255, 178), (254, 204, 92), (253, 141, 60), (227, 26, 28)],
                 'YlOrRd5': [(255, 255, 178), (254, 204, 92), (253, 141, 60), (240, 59, 32), (189, 0, 38)],
                 'YlOrRd6': [(255, 255, 178), (254, 217, 118), (254, 178, 76), (253, 141, 60), (240, 59, 32), (189, 0, 38)],
                 'YlOrRd7': [(255, 255, 178), (254, 217, 118), (254, 178, 76), (253, 141, 60), (252, 78, 42), (227, 26, 28), (177, 0, 38)],
                 'YlOrRd8': [(255, 255, 204), (255, 237, 160), (254, 217, 118), (254, 178, 76), (253, 141, 60), (252, 78, 42), (227, 26, 28), (177, 0, 38)],
                 'YlOrRd9': [(255, 255, 204), (255, 237, 160), (254, 217, 118), (254, 178, 76), (253, 141, 60), (252, 78, 42), (227, 26, 28), (189, 0, 38), (128, 0, 38)],
                 'YlOrBr3': [(255, 247, 188), (254, 196, 79), (217, 95, 14)],
                 'YlOrBr4': [(255, 255, 212), (254, 217, 142), (254, 153, 41), (204, 76, 2)],
                 'YlOrBr5': [(255, 255, 212), (254, 217, 142), (254, 153, 41), (217, 95, 14), (153, 52, 4)],
                 'YlOrBr6': [(255, 255, 212), (254, 227, 145), (254, 196, 79), (254, 153, 41), (217, 95, 14), (153, 52, 4)],
                 'YlOrBr7': [(255, 255, 212), (254, 227, 145), (254, 196, 79), (254, 153, 41), (236, 112, 20), (204, 76, 2), (140, 45, 4)],
                 'YlOrBr8': [(255, 255, 229), (255, 247, 188), (254, 227, 145), (254, 196, 79), (254, 153, 41), (236, 112, 20), (204, 76, 2), (140, 45, 4)],
                 'YlOrBr9': [(255, 255, 229), (255, 247, 188), (254, 227, 145), (254, 196, 79), (254, 153, 41), (236, 112, 20), (204, 76, 2), (153, 52, 4), (102, 37, 6)],
                 'Purples3': [(239, 237, 245), (188, 189, 220), (117, 107, 177)],
                 'Purples4': [(242, 240, 247), (203, 201, 226), (158, 154, 200), (106, 81, 163)],
                 'Purples5': [(242, 240, 247), (203, 201, 226), (158, 154, 200), (117, 107, 177), (84, 39, 143)],
                 'Purples6': [(242, 240, 247), (218, 218, 235), (188, 189, 220), (158, 154, 200), (117, 107, 177), (84, 39, 143)],
                 'Purples7': [(242, 240, 247), (218, 218, 235), (188, 189, 220), (158, 154, 200), (128, 125, 186), (106, 81, 163), (74, 20, 134)],
                 'Purples8': [(252, 251, 253), (239, 237, 245), (218, 218, 235), (188, 189, 220), (158, 154, 200), (128, 125, 186), (106, 81, 163), (74, 20, 134)],
                 'Purples9': [(252, 251, 253), (239, 237, 245), (218, 218, 235), (188, 189, 220), (158, 154, 200), (128, 125, 186), (106, 81, 163), (84, 39, 143), (63, 0, 125)],
                 'Blues3': [(222, 235, 247), (158, 202, 225), (49, 130, 189)],
                 'Blues4': [(239, 243, 255), (189, 215, 231), (107, 174, 214), (33, 113, 181)],
                 'Blues5': [(239, 243, 255), (189, 215, 231), (107, 174, 214), (49, 130, 189), (8, 81, 156)],
                 'Blues6': [(239, 243, 255), (198, 219, 239), (158, 202, 225), (107, 174, 214), (49, 130, 189), (8, 81, 156)],
                 'Blues7': [(239, 243, 255), (198, 219, 239), (158, 202, 225), (107, 174, 214), (66, 146, 198), (33, 113, 181), (8, 69, 148)],
                 'Blues8': [(247, 251, 255), (222, 235, 247), (198, 219, 239), (158, 202, 225), (107, 174, 214), (66, 146, 198), (33, 113, 181), (8, 69, 148)],
                 'Blues9': [(247, 251, 255), (222, 235, 247), (198, 219, 239), (158, 202, 225), (107, 174, 214), (66, 146, 198), (33, 113, 181), (8, 81, 156), (8, 48, 107)],
                 'Greens3': [(229, 245, 224), (161, 217, 155), (49, 163, 84)],
                 'Greens4': [(237, 248, 233), (186, 228, 179), (116, 196, 118), (35, 139, 69)],
                 'Greens5': [(237, 248, 233), (186, 228, 179), (116, 196, 118), (49, 163, 84), (0, 109, 44)],
                 'Greens6': [(237, 248, 233), (199, 233, 192), (161, 217, 155), (116, 196, 118), (49, 163, 84), (0, 109, 44)],
                 'Greens7': [(237, 248, 233), (199, 233, 192), (161, 217, 155), (116, 196, 118), (65, 171, 93), (35, 139, 69), (0, 90, 50)],
                 'Greens8': [(247, 252, 245), (229, 245, 224), (199, 233, 192), (161, 217, 155), (116, 196, 118), (65, 171, 93), (35, 139, 69), (0, 90, 50)],
                 'Greens9': [(247, 252, 245), (229, 245, 224), (199, 233, 192), (161, 217, 155), (116, 196, 118), (65, 171, 93), (35, 139, 69), (0, 109, 44), (0, 68, 27)],
                 'Oranges3': [(254, 230, 206), (253, 174, 107), (230, 85, 13)],
                 'Oranges4': [(254, 237, 222), (253, 190, 133), (253, 141, 60), (217, 71, 1)],
                 'Oranges5': [(254, 237, 222), (253, 190, 133), (253, 141, 60), (230, 85, 13), (166, 54, 3)],
                 'Oranges6': [(254, 237, 222), (253, 208, 162), (253, 174, 107), (253, 141, 60), (230, 85, 13), (166, 54, 3)],
                 'Oranges7': [(254, 237, 222), (253, 208, 162), (253, 174, 107), (253, 141, 60), (241, 105, 19), (217, 72, 1), (140, 45, 4)],
                 'Oranges8': [(255, 245, 235), (254, 230, 206), (253, 208, 162), (253, 174, 107), (253, 141, 60), (241, 105, 19), (217, 72, 1), (140, 45, 4)],
                 'Oranges9': [(255, 245, 235), (254, 230, 206), (253, 208, 162), (253, 174, 107), (253, 141, 60), (241, 105, 19), (217, 72, 1), (166, 54, 3), (127, 39, 4)],
                 'Reds3': [(254, 224, 210), (252, 146, 114), (222, 45, 38)],
                 'Reds4': [(254, 229, 217), (252, 174, 145), (251, 106, 74), (203, 24, 29)],
                 'Reds5': [(254, 229, 217), (252, 174, 145), (251, 106, 74), (222, 45, 38), (165, 15, 21)],
                 'Reds6': [(254, 229, 217), (252, 187, 161), (252, 146, 114), (251, 106, 74), (222, 45, 38), (165, 15, 21)],
                 'Reds7': [(254, 229, 217), (252, 187, 161), (252, 146, 114), (251, 106, 74), (239, 59, 44), (203, 24, 29), (153, 0, 13)],
                 'Reds8': [(255, 245, 240), (254, 224, 210), (252, 187, 161), (252, 146, 114), (251, 106, 74), (239, 59, 44), (203, 24, 29), (153, 0, 13)],
                 'Reds9': [(255, 245, 240), (254, 224, 210), (252, 187, 161), (252, 146, 114), (251, 106, 74), (239, 59, 44), (203, 24, 29), (165, 15, 21), (103, 0, 13)],
                 'Greys3': [(240, 240, 240), (189, 189, 189), (99, 99, 99)],
                 'Greys4': [(247, 247, 247), (204, 204, 204), (150, 150, 150), (82, 82, 82)],
                 'Greys5': [(247, 247, 247), (204, 204, 204), (150, 150, 150), (99, 99, 99), (37, 37, 37)],
                 'Greys6': [(247, 247, 247), (217, 217, 217), (189, 189, 189), (150, 150, 150), (99, 99, 99), (37, 37, 37)],
                 'Greys7': [(247, 247, 247), (217, 217, 217), (189, 189, 189), (150, 150, 150), (115, 115, 115), (82, 82, 82), (37, 37, 37)],
                 'Greys8': [(255, 255, 255), (240, 240, 240), (217, 217, 217), (189, 189, 189), (150, 150, 150), (115, 115, 115), (82, 82, 82), (37, 37, 37)],
                 'Greys9': [(255, 255, 255), (240, 240, 240), (217, 217, 217), (189, 189, 189), (150, 150, 150), (115, 115, 115), (82, 82, 82), (37, 37, 37), (0, 0, 0)],
                 'PuOr3': [(241, 163, 64), (247, 247, 247), (153, 142, 195)],
                 'PuOr4': [(230, 97, 1), (253, 184, 99), (178, 171, 210), (94, 60, 153)],
                 'PuOr5': [(230, 97, 1), (253, 184, 99), (247, 247, 247), (178, 171, 210), (94, 60, 153)],
                 'PuOr6': [(179, 88, 6), (241, 163, 64), (254, 224, 182), (216, 218, 235), (153, 142, 195), (84, 39, 136)],
                 'PuOr7': [(179, 88, 6), (241, 163, 64), (254, 224, 182), (247, 247, 247), (216, 218, 235), (153, 142, 195), (84, 39, 136)],
                 'PuOr8': [(179, 88, 6), (224, 130, 20), (253, 184, 99), (254, 224, 182), (216, 218, 235), (178, 171, 210), (128, 115, 172), (84, 39, 136)],
                 'PuOr9': [(179, 88, 6), (224, 130, 20), (253, 184, 99), (254, 224, 182), (247, 247, 247), (216, 218, 235), (178, 171, 210), (128, 115, 172), (84, 39, 136)],
                 'PuOr10': [(127, 59, 8), (179, 88, 6), (224, 130, 20), (253, 184, 99), (254, 224, 182), (216, 218, 235), (178, 171, 210), (128, 115, 172), (84, 39, 136), (45, 0, 75)],
                 'PuOr11': [(127, 59, 8), (179, 88, 6), (224, 130, 20), (253, 184, 99), (254, 224, 182), (247, 247, 247), (216, 218, 235), (178, 171, 210), (128, 115, 172), (84, 39, 136), (45, 0, 75)],
                 'BrBG3': [(216, 179, 101), (245, 245, 245), (90, 180, 172)],
                 'BrBG4': [(166, 97, 26), (223, 194, 125), (128, 205, 193), (1, 133, 113)],
                 'BrBG5': [(166, 97, 26), (223, 194, 125), (245, 245, 245), (128, 205, 193), (1, 133, 113)],
                 'BrBG6': [(140, 81, 10), (216, 179, 101), (246, 232, 195), (199, 234, 229), (90, 180, 172), (1, 102, 94)],
                 'BrBG7': [(140, 81, 10), (216, 179, 101), (246, 232, 195), (245, 245, 245), (199, 234, 229), (90, 180, 172), (1, 102, 94)],
                 'BrBG8': [(140, 81, 10), (191, 129, 45), (223, 194, 125), (246, 232, 195), (199, 234, 229), (128, 205, 193), (53, 151, 143), (1, 102, 94)],
                 'BrBG9': [(140, 81, 10), (191, 129, 45), (223, 194, 125), (246, 232, 195), (245, 245, 245), (199, 234, 229), (128, 205, 193), (53, 151, 143), (1, 102, 94)],
                 'BrBG10': [(84, 48, 5), (140, 81, 10), (191, 129, 45), (223, 194, 125), (246, 232, 195), (199, 234, 229), (128, 205, 193), (53, 151, 143), (1, 102, 94), (0, 60, 48)],
                 'BrBG11': [(84, 48, 5), (140, 81, 10), (191, 129, 45), (223, 194, 125), (246, 232, 195), (245, 245, 245), (199, 234, 229), (128, 205, 193), (53, 151, 143), (1, 102, 94), (0, 60, 48)],
                 'PRGn3': [(175, 141, 195), (247, 247, 247), (127, 191, 123)],
                 'PRGn4': [(123, 50, 148), (194, 165, 207), (166, 219, 160), (0, 136, 55)],
                 'PRGn5': [(123, 50, 148), (194, 165, 207), (247, 247, 247), (166, 219, 160), (0, 136, 55)],
                 'PRGn6': [(118, 42, 131), (175, 141, 195), (231, 212, 232), (217, 240, 211), (127, 191, 123), (27, 120, 55)],
                 'PRGn7': [(118, 42, 131), (175, 141, 195), (231, 212, 232), (247, 247, 247), (217, 240, 211), (127, 191, 123), (27, 120, 55)],
                 'PRGn8': [(118, 42, 131), (153, 112, 171), (194, 165, 207), (231, 212, 232), (217, 240, 211), (166, 219, 160), (90, 174, 97), (27, 120, 55)],
                 'PRGn9': [(118, 42, 131), (153, 112, 171), (194, 165, 207), (231, 212, 232), (247, 247, 247), (217, 240, 211), (166, 219, 160), (90, 174, 97), (27, 120, 55)],
                 'PRGn10': [(64, 0, 75), (118, 42, 131), (153, 112, 171), (194, 165, 207), (231, 212, 232), (217, 240, 211), (166, 219, 160), (90, 174, 97), (27, 120, 55), (0, 68, 27)],
                 'PRGn11': [(64, 0, 75), (118, 42, 131), (153, 112, 171), (194, 165, 207), (231, 212, 232), (247, 247, 247), (217, 240, 211), (166, 219, 160), (90, 174, 97), (27, 120, 55), (0, 68, 27)],
                 'PiYG3': [(233, 163, 201), (247, 247, 247), (161, 215, 106)],
                 'PiYG4': [(208, 28, 139), (241, 182, 218), (184, 225, 134), (77, 172, 38)],
                 'PiYG5': [(208, 28, 139), (241, 182, 218), (247, 247, 247), (184, 225, 134), (77, 172, 38)],
                 'PiYG6': [(197, 27, 125), (233, 163, 201), (253, 224, 239), (230, 245, 208), (161, 215, 106), (77, 146, 33)],
                 'PiYG7': [(197, 27, 125), (233, 163, 201), (253, 224, 239), (247, 247, 247), (230, 245, 208), (161, 215, 106), (77, 146, 33)],
                 'PiYG8': [(197, 27, 125), (222, 119, 174), (241, 182, 218), (253, 224, 239), (230, 245, 208), (184, 225, 134), (127, 188, 65), (77, 146, 33)],
                 'PiYG9': [(197, 27, 125), (222, 119, 174), (241, 182, 218), (253, 224, 239), (247, 247, 247), (230, 245, 208), (184, 225, 134), (127, 188, 65), (77, 146, 33)],
                 'PiYG10': [(142, 1, 82), (197, 27, 125), (222, 119, 174), (241, 182, 218), (253, 224, 239), (230, 245, 208), (184, 225, 134), (127, 188, 65), (77, 146, 33), (39, 100, 25)],
                 'PiYG11': [(142, 1, 82), (197, 27, 125), (222, 119, 174), (241, 182, 218), (253, 224, 239), (247, 247, 247), (230, 245, 208), (184, 225, 134), (127, 188, 65), (77, 146, 33), (39, 100, 25)],
                 'RdBu3': [(239, 138, 98), (247, 247, 247), (103, 169, 207)],
                 'RdBu4': [(202, 0, 32), (244, 165, 130), (146, 197, 222), (5, 113, 176)],
                 'RdBu5': [(202, 0, 32), (244, 165, 130), (247, 247, 247), (146, 197, 222), (5, 113, 176)],
                 'RdBu6': [(178, 24, 43), (239, 138, 98), (253, 219, 199), (209, 229, 240), (103, 169, 207), (33, 102, 172)],
                 'RdBu7': [(178, 24, 43), (239, 138, 98), (253, 219, 199), (247, 247, 247), (209, 229, 240), (103, 169, 207), (33, 102, 172)],
                 'RdBu8': [(178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (209, 229, 240), (146, 197, 222), (67, 147, 195), (33, 102, 172)],
                 'RdBu9': [(178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (247, 247, 247), (209, 229, 240), (146, 197, 222), (67, 147, 195), (33, 102, 172)],
                 'RdBu10': [(103, 0, 31), (178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (209, 229, 240), (146, 197, 222), (67, 147, 195), (33, 102, 172), (5, 48, 97)],
                 'RdBu11': [(103, 0, 31), (178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (247, 247, 247), (209, 229, 240), (146, 197, 222), (67, 147, 195), (33, 102, 172), (5, 48, 97)],
                 'RdGy3': [(239, 138, 98), (255, 255, 255), (153, 153, 153)],
                 'RdGy4': [(202, 0, 32), (244, 165, 130), (186, 186, 186), (64, 64, 64)],
                 'RdGy5': [(202, 0, 32), (244, 165, 130), (255, 255, 255), (186, 186, 186), (64, 64, 64)],
                 'RdGy6': [(178, 24, 43), (239, 138, 98), (253, 219, 199), (224, 224, 224), (153, 153, 153), (77, 77, 77)],
                 'RdGy7': [(178, 24, 43), (239, 138, 98), (253, 219, 199), (255, 255, 255), (224, 224, 224), (153, 153, 153), (77, 77, 77)],
                 'RdGy8': [(178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (224, 224, 224), (186, 186, 186), (135, 135, 135), (77, 77, 77)],
                 'RdGy9': [(178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (255, 255, 255), (224, 224, 224), (186, 186, 186), (135, 135, 135), (77, 77, 77)],
                 'RdGy10': [(103, 0, 31), (178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (224, 224, 224), (186, 186, 186), (135, 135, 135), (77, 77, 77), (26, 26, 26)],
                 'RdGy11': [(103, 0, 31), (178, 24, 43), (214, 96, 77), (244, 165, 130), (253, 219, 199), (255, 255, 255), (224, 224, 224), (186, 186, 186), (135, 135, 135), (77, 77, 77), (26, 26, 26)],
                 'RdYlBu3': [(252, 141, 89), (255, 255, 191), (145, 191, 219)],
                 'RdYlBu4': [(215, 25, 28), (253, 174, 97), (171, 217, 233), (44, 123, 182)],
                 'RdYlBu5': [(215, 25, 28), (253, 174, 97), (255, 255, 191), (171, 217, 233), (44, 123, 182)],
                 'RdYlBu6': [(215, 48, 39), (252, 141, 89), (254, 224, 144), (224, 243, 248), (145, 191, 219), (69, 117, 180)],
                 'RdYlBu7': [(215, 48, 39), (252, 141, 89), (254, 224, 144), (255, 255, 191), (224, 243, 248), (145, 191, 219), (69, 117, 180)],
                 'RdYlBu8': [(215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 144), (224, 243, 248), (171, 217, 233), (116, 173, 209), (69, 117, 180)],
                 'RdYlBu9': [(215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 144), (255, 255, 191), (224, 243, 248), (171, 217, 233), (116, 173, 209), (69, 117, 180)],
                 'RdYlBu10': [(165, 0, 38), (215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 144), (224, 243, 248), (171, 217, 233), (116, 173, 209), (69, 117, 180), (49, 54, 149)],
                 'RdYlBu11': [(165, 0, 38), (215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 144), (255, 255, 191), (224, 243, 248), (171, 217, 233), (116, 173, 209), (69, 117, 180), (49, 54, 149)],
                 'Spectral3': [(252, 141, 89), (255, 255, 191), (153, 213, 148)],
                 'Spectral4': [(215, 25, 28), (253, 174, 97), (171, 221, 164), (43, 131, 186)],
                 'Spectral5': [(215, 25, 28), (253, 174, 97), (255, 255, 191), (171, 221, 164), (43, 131, 186)],
                 'Spectral6': [(213, 62, 79), (252, 141, 89), (254, 224, 139), (230, 245, 152), (153, 213, 148), (50, 136, 189)],
                 'Spectral7': [(213, 62, 79), (252, 141, 89), (254, 224, 139), (255, 255, 191), (230, 245, 152), (153, 213, 148), (50, 136, 189)],
                 'Spectral8': [(213, 62, 79), (244, 109, 67), (253, 174, 97), (254, 224, 139), (230, 245, 152), (171, 221, 164), (102, 194, 165), (50, 136, 189)],
                 'Spectral9': [(213, 62, 79), (244, 109, 67), (253, 174, 97), (254, 224, 139), (255, 255, 191), (230, 245, 152), (171, 221, 164), (102, 194, 165), (50, 136, 189)],
                 'Spectral10': [(158, 1, 66), (213, 62, 79), (244, 109, 67), (253, 174, 97), (254, 224, 139), (230, 245, 152), (171, 221, 164), (102, 194, 165), (50, 136, 189), (94, 79, 162)],
                 'Spectral11': [(158, 1, 66), (213, 62, 79), (244, 109, 67), (253, 174, 97), (254, 224, 139), (255, 255, 191), (230, 245, 152), (171, 221, 164), (102, 194, 165), (50, 136, 189), (94, 79, 162)],
                 'RdYlGn3': [(252, 141, 89), (255, 255, 191), (145, 207, 96)],
                 'RdYlGn4': [(215, 25, 28), (253, 174, 97), (166, 217, 106), (26, 150, 65)],
                 'RdYlGn5': [(215, 25, 28), (253, 174, 97), (255, 255, 191), (166, 217, 106), (26, 150, 65)],
                 'RdYlGn6': [(215, 48, 39), (252, 141, 89), (254, 224, 139), (217, 239, 139), (145, 207, 96), (26, 152, 80)],
                 'RdYlGn7': [(215, 48, 39), (252, 141, 89), (254, 224, 139), (255, 255, 191), (217, 239, 139), (145, 207, 96), (26, 152, 80)],
                 'RdYlGn8': [(215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 139), (217, 239, 139), (166, 217, 106), (102, 189, 99), (26, 152, 80)],
                 'RdYlGn9': [(215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 139), (255, 255, 191), (217, 239, 139), (166, 217, 106), (102, 189, 99), (26, 152, 80)],
                 'RdYlGn10': [(165, 0, 38), (215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 139), (217, 239, 139), (166, 217, 106), (102, 189, 99), (26, 152, 80), (0, 104, 55)],
                 'RdYlGn11': [(165, 0, 38), (215, 48, 39), (244, 109, 67), (253, 174, 97), (254, 224, 139), (255, 255, 191), (217, 239, 139), (166, 217, 106), (102, 189, 99), (26, 152, 80), (0, 104, 55)],
                 'Set33': [(141, 211, 199), (255, 255, 179), (190, 186, 218)],
                 'Set34': [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114)],
                 'Set35': [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211)],
                 'Set36': [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98)],
                 'Set37': [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98), (179, 222, 105)],
                 'Set38': [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98), (179, 222, 105), (252, 205, 229)],
                 'Set39': [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98), (179, 222, 105), (252, 205, 229), (217, 217, 217)],
                 'Set310': [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98), (179, 222, 105), (252, 205, 229), (217, 217, 217), (188, 128, 189)],
                 'Set311': [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98), (179, 222, 105), (252, 205, 229), (217, 217, 217), (188, 128, 189), (204, 235, 197)],
                 'Set312': [(141, 211, 199), (255, 255, 179), (190, 186, 218), (251, 128, 114), (128, 177, 211), (253, 180, 98), (179, 222, 105), (252, 205, 229), (217, 217, 217), (188, 128, 189), (204, 235, 197), (255, 237, 111)],
                 'Pastel13': [(251, 180, 174), (179, 205, 227), (204, 235, 197)],
                 'Pastel14': [(251, 180, 174), (179, 205, 227), (204, 235, 197), (222, 203, 228)],
                 'Pastel15': [(251, 180, 174), (179, 205, 227), (204, 235, 197), (222, 203, 228), (254, 217, 166)],
                 'Pastel16': [(251, 180, 174), (179, 205, 227), (204, 235, 197), (222, 203, 228), (254, 217, 166), (255, 255, 204)],
                 'Pastel17': [(251, 180, 174), (179, 205, 227), (204, 235, 197), (222, 203, 228), (254, 217, 166), (255, 255, 204), (229, 216, 189)],
                 'Pastel18': [(251, 180, 174), (179, 205, 227), (204, 235, 197), (222, 203, 228), (254, 217, 166), (255, 255, 204), (229, 216, 189), (253, 218, 236)],
                 'Pastel19': [(251, 180, 174), (179, 205, 227), (204, 235, 197), (222, 203, 228), (254, 217, 166), (255, 255, 204), (229, 216, 189), (253, 218, 236), (242, 242, 242)],
                 'Set13': [(228, 26, 28), (55, 126, 184), (77, 175, 74)],
                 'Set14': [(228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163)],
                 'Set15': [(228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163), (255, 127, 0)],
                 'Set16': [(228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163), (255, 127, 0), (255, 255, 51)],
                 'Set17': [(228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163), (255, 127, 0), (255, 255, 51), (166, 86, 40)],
                 'Set18': [(228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163), (255, 127, 0), (255, 255, 51), (166, 86, 40), (247, 129, 191)],
                 'Set19': [(228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163), (255, 127, 0), (255, 255, 51), (166, 86, 40), (247, 129, 191), (153, 153, 153)],
                 'Pastel23': [(179, 226, 205), (253, 205, 172), (203, 213, 232)],
                 'Pastel24': [(179, 226, 205), (253, 205, 172), (203, 213, 232), (244, 202, 228)],
                 'Pastel25': [(179, 226, 205), (253, 205, 172), (203, 213, 232), (244, 202, 228), (230, 245, 201)],
                 'Pastel26': [(179, 226, 205), (253, 205, 172), (203, 213, 232), (244, 202, 228), (230, 245, 201), (255, 242, 174)],
                 'Pastel27': [(179, 226, 205), (253, 205, 172), (203, 213, 232), (244, 202, 228), (230, 245, 201), (255, 242, 174), (241, 226, 204)],
                 'Pastel28': [(179, 226, 205), (253, 205, 172), (203, 213, 232), (244, 202, 228), (230, 245, 201), (255, 242, 174), (241, 226, 204), (204, 204, 204)],
                 'Set23': [(102, 194, 165), (252, 141, 98), (141, 160, 203)],
                 'Set24': [(102, 194, 165), (252, 141, 98), (141, 160, 203), (231, 138, 195)],
                 'Set25': [(102, 194, 165), (252, 141, 98), (141, 160, 203), (231, 138, 195), (166, 216, 84)],
                 'Set26': [(102, 194, 165), (252, 141, 98), (141, 160, 203), (231, 138, 195), (166, 216, 84), (255, 217, 47)],
                 'Set27': [(102, 194, 165), (252, 141, 98), (141, 160, 203), (231, 138, 195), (166, 216, 84), (255, 217, 47), (229, 196, 148)],
                 'Set28': [(102, 194, 165), (252, 141, 98), (141, 160, 203), (231, 138, 195), (166, 216, 84), (255, 217, 47), (229, 196, 148), (179, 179, 179)],
                 'Dark23': [(27, 158, 119), (217, 95, 2), (117, 112, 179)],
                 'Dark24': [(27, 158, 119), (217, 95, 2), (117, 112, 179), (231, 41, 138)],
                 'Dark25': [(27, 158, 119), (217, 95, 2), (117, 112, 179), (231, 41, 138), (102, 166, 30)],
                 'Dark26': [(27, 158, 119), (217, 95, 2), (117, 112, 179), (231, 41, 138), (102, 166, 30), (230, 171, 2)],
                 'Dark27': [(27, 158, 119), (217, 95, 2), (117, 112, 179), (231, 41, 138), (102, 166, 30), (230, 171, 2), (166, 118, 29)],
                 'Dark28': [(27, 158, 119), (217, 95, 2), (117, 112, 179), (231, 41, 138), (102, 166, 30), (230, 171, 2), (166, 118, 29), (102, 102, 102)],
                 'Paired3': [(166, 206, 227), (31, 120, 180), (178, 223, 138)],
                 'Paired4': [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44)],
                 'Paired5': [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153)],
                 'Paired6': [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28)],
                 'Paired7': [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28), (253, 191, 111)],
                 'Paired8': [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28), (253, 191, 111), (255, 127, 0)],
                 'Paired9': [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28), (253, 191, 111), (255, 127, 0), (202, 178, 214)],
                 'Paired10': [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28), (253, 191, 111), (255, 127, 0), (202, 178, 214), (106, 61, 154)],
                 'Paired11': [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28), (253, 191, 111), (255, 127, 0), (202, 178, 214), (106, 61, 154), (255, 255, 153)],
                 'Paired12': [(166, 206, 227), (31, 120, 180), (178, 223, 138), (51, 160, 44), (251, 154, 153), (227, 26, 28), (253, 191, 111), (255, 127, 0), (202, 178, 214), (106, 61, 154), (255, 255, 153), (177, 89, 40)],
                 'Accent3': [(127, 201, 127), (190, 174, 212), (253, 192, 134)],
                 'Accent4': [(127, 201, 127), (190, 174, 212), (253, 192, 134), (255, 255, 153)],
                 'Accent5': [(127, 201, 127), (190, 174, 212), (253, 192, 134), (255, 255, 153), (56, 108, 176)],
                 'Accent6': [(127, 201, 127), (190, 174, 212), (253, 192, 134), (255, 255, 153), (56, 108, 176), (240, 2, 127)],
                 'Accent7': [(127, 201, 127), (190, 174, 212), (253, 192, 134), (255, 255, 153), (56, 108, 176), (240, 2, 127), (191, 91, 23)],
                 'Accent8': [(127, 201, 127), (190, 174, 212), (253, 192, 134), (255, 255, 153), (56, 108, 176), (240, 2, 127), (191, 91, 23), (102, 102, 102)],
               }
