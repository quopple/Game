from panda3d.core import (
    GeomVertexFormat, GeomVertexData,
    Geom, GeomTriangles, GeomVertexWriter,
    LVector3,
    Texture, GeomNode,
) 

# You can't normalize inline so this is a helper function
def normalized(*args):
    myVec = LVector3(*args)
    myVec.normalize()
    return myVec

class Cube():
    def __init__(self):
        pass
    @staticmethod
    def makeSquare(x1, y1, z1, x2, y2, z2):
        format = GeomVertexFormat.getV3n3cpt2()
        vdata = GeomVertexData('square', format, Geom.UHDynamic)

        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')
        texcoord = GeomVertexWriter(vdata, 'texcoord')

        # make sure we draw the sqaure in the right plane
        if x1 != x2:
            vertex.addData3(x1, y1, z1)
            vertex.addData3(x2, y1, z1)
            vertex.addData3(x2, y2, z2)
            vertex.addData3(x1, y2, z2)

            normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
            normal.addData3(normalized(2 * x2 - 1, 2 * y1 - 1, 2 * z1 - 1))
            normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
            normal.addData3(normalized(2 * x1 - 1, 2 * y2 - 1, 2 * z2 - 1))

        else:
            vertex.addData3(x1, y1, z1)
            vertex.addData3(x2, y2, z1)
            vertex.addData3(x2, y2, z2)
            vertex.addData3(x1, y1, z2)

            normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z1 - 1))
            normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z1 - 1))
            normal.addData3(normalized(2 * x2 - 1, 2 * y2 - 1, 2 * z2 - 1))
            normal.addData3(normalized(2 * x1 - 1, 2 * y1 - 1, 2 * z2 - 1))

        # adding different colors to the vertex for visibility
        # color.addData4f(1.0, 0.0, 0.0, 1.0)
        # color.addData4f(0.0, 1.0, 0.0, 1.0)
        # color.addData4f(0.0, 0.0, 1.0, 1.0)
        # color.addData4f(1.0, 0.0, 1.0, 1.0)

        color.addData4f(1.0, 1.0, 1.0, 1.0)
        color.addData4f(1.0, 1.0, 1.0, 1.0)
        color.addData4f(1.0, 1.0, 1.0, 1.0)
        color.addData4f(1.0, 1.0, 1.0, 1.0)

        texcoord.addData2f(0.0, 1.0)
        texcoord.addData2f(0.0, 0.0)
        texcoord.addData2f(1.0, 0.0)
        texcoord.addData2f(1.0, 1.0)

        # Quads aren't directly supported by the Geom interface
        # you might be interested in the CardMaker class if you are
        # interested in rectangle though
        tris = GeomTriangles(Geom.UHDynamic)
        tris.addVertices(0, 1, 3)
        tris.addVertices(1, 2, 3)

        square = Geom(vdata)
        square.addPrimitive(tris)
        return square
    @staticmethod
    def makeCube(a=1,parent=None):
        # Note: it isn't particularly efficient to make every face as a separate Geom.
        # instead, it would be better to create one Geom holding all of the faces.
        square0 = Cube.makeSquare(-a, -a, -a, a, -a, a)
        square1 = Cube.makeSquare(-a, a, -a, a, a, a)
        square2 = Cube.makeSquare(-a, a, a, a, -a, a)
        square3 = Cube.makeSquare(-a, a, -a, a, -a, -a)
        square4 = Cube.makeSquare(-a, -a, -a, -a, a, a)
        square5 = Cube.makeSquare(a, -a, -a, a, a, a)
        snode = GeomNode('square')
        snode.addGeom(square0)
        snode.addGeom(square1)
        snode.addGeom(square2)
        snode.addGeom(square3)
        snode.addGeom(square4)
        snode.addGeom(square5)

        if parent==None:
            cube =  render.attachNewNode(snode)
        else:
            cube = parent.attachNewNode(snode)
        cube.setTwoSided(True)
        return cube

