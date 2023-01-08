import NemAll_Python_Geometry as geometry
import NemAll_Python_BaseElements as base_element
import NemAll_Python_BasisElements as basis_element
import NemAll_Python_Utility as utility
import GeometryValidate as val
from HandleDirection import HandleDirection
from HandleProperties import HandleProperties


def check_allplan_version(build_ele, version):
    del build_ele
    del version
    return True


def create_element(build_ele, doc):
    el = Lab2_Beam(doc)
    return el.create(build_ele)


def move_handle(build_ele, handle_prop, input_pnt, doc):
    build_ele.change_property(handle_prop, input_pnt)
    return create_element(build_ele, doc)


class Lab2_Beam:

    def __init__(self, doc):
        self.model_ele_list = []
        self.handle_list = []
        self.document = doc

    def create(self, build_ele):
        self.up(build_ele)
        self.handles(build_ele)
        return (self.model_ele_list, self.handle_list)

    def down(self, build_ele):
        get_info = self.get(build_ele)
        figure = geometry.BRep3D.CreateCuboid(geometry.AxisPlacement3D(geometry.Point3D(0, 0, 0), geometry.Vector3D(
            1, 0, 0), geometry.Vector3D(0, 0, 1)), get_info[0], get_info[1], get_info[2])
        figure_2 = geometry.BRep3D.CreateCuboid(geometry.AxisPlacement3D(geometry.Point3D(0, 0, 0), geometry.Vector3D(
            1, 0, 0), geometry.Vector3D(0, 0, 1)), get_info[0], get_info[1], get_info[2])
        cut_weight = build_ele.sectiont.value
        cut_buttom = build_ele.sectionb.value

        if cut_weight > 0:
            figure_edges = utility.VecSizeTList()
            figure_edges.append(1)
            figure_edges.append(3)
            error, figure = geometry.ChamferCalculus.Calculate(
                figure, figure_edges, cut_weight, False)

            if not val.polyhedron(error):
                return

        if cut_buttom > 0:
            figure_edges_2 = utility.VecSizeTList()
            figure_edges_2.append(8)
            figure_edges_2.append(10)
            error, figure_2 = geometry.ChamferCalculus.Calculate(
                figure_2, figure_edges_2, cut_buttom, False)

            if not val.polyhedron(error):
                return

        error, end_figure = geometry.MakeIntersection(figure, figure_2)
        return end_figure

    def center(self, build_ele):
        get_info = self.get(build_ele)
        figure = geometry.BRep3D.CreateCuboid(geometry.AxisPlacement3D(geometry.Point3D(
            get_info[0] / 2 - get_info[3] / 2, 0, get_info[2]), geometry.Vector3D(1, 0, 0), geometry.Vector3D(0, 0, 1)), get_info[3], get_info[1], get_info[4])
        figure_1 = geometry.BRep3D.CreateCylinder(geometry.AxisPlacement3D(geometry.Point3D(
            get_info[5], get_info[1] / 8, get_info[2] + get_info[4] / 2), geometry.Vector3D(0, 0, 1), geometry.Vector3D(1, 0, 0)), get_info[6], get_info[3])
        figure_2 = geometry.BRep3D.CreateCylinder(geometry.AxisPlacement3D(geometry.Point3D(
            get_info[5], get_info[1] - get_info[1] / 8, get_info[2] + get_info[4] / 2), geometry.Vector3D(0, 0, 1), geometry.Vector3D(1, 0, 0)), get_info[6], get_info[3])
        error, figure = geometry.MakeSubtraction(figure, figure_1)
        error, figure = geometry.MakeSubtraction(figure, figure_2)
        error, end_figure = geometry.MakeUnion(
            figure, self.down(build_ele))
        return end_figure

    def up(self, build_ele):
        get_info = self.get(build_ele)
        figure = geometry.BRep3D.CreateCuboid(geometry.AxisPlacement3D(geometry.Point3D(
            0 - (get_info[7] - get_info[0]) / 2, 0, get_info[2] + get_info[4]), geometry.Vector3D(1, 0, 0), geometry.Vector3D(0, 0, 1)), get_info[7], get_info[1], get_info[8])
        pl = geometry.BRep3D.CreateCuboid(geometry.AxisPlacement3D(geometry.Point3D(get_info[9] - (get_info[7] - get_info[0]) / 2, 0, get_info[2] + get_info[4] + get_info[8]), geometry.Vector3D(
            1, 0, 0), geometry.Vector3D(0, 0, 1)), get_info[7] - get_info[9]*2, get_info[1], get_info[10])
        com_prop = base_element.CommonProperties()
        com_prop.GetGlobalProperties()
        com_prop.Pen = 1
        com_prop.Color = get_info[11]
        top = get_info[12]

        if top > 0:
            figure_edges_2 = utility.VecSizeTList()
            figure_edges_2.append(8)
            figure_edges_2.append(10)
            error, figure = geometry.ChamferCalculus.Calculate(
                figure, figure_edges_2, top, False)

            if not val.polyhedron(error):
                return

        error, end_figure = geometry.MakeUnion(figure, self.center(build_ele))
        error, end_figure = geometry.MakeUnion(end_figure, pl)
        self.model_ele_list.append(
            basis_element.ModelElement3D(com_prop, end_figure))

    def handles(self, build_ele):
        get_info = self.get(build_ele)
        handle_1 = geometry.Point3D(
            get_info[0] / 2, get_info[1], get_info[4] + get_info[2])
        self.handle_list.append(HandleProperties("middlehe", geometry.Point3D(handle_1.X, handle_1.Y, handle_1.Z), geometry.Point3D(
            handle_1.X, handle_1.Y, handle_1.Z - get_info[4]), [("middlehe", HandleDirection.z_dir)], HandleDirection.z_dir, False))
        handle_2 = geometry.Point3D(get_info[0] / 2, 0, get_info[2] / 2)
        self.handle_list.append(HandleProperties("len", geometry.Point3D(handle_2.X, handle_2.Y + get_info[1], handle_2.Z), geometry.Point3D(
            handle_2.X, handle_2.Y, handle_2.Z), [("len", HandleDirection.y_dir)], HandleDirection.y_dir, False))
        handle_3 = geometry.Point3D(
            0, get_info[1], (get_info[2] - get_info[5]) / 2)
        self.handle_list.append(HandleProperties("wid", geometry.Point3D(handle_3.X + get_info[0], handle_3.Y, handle_3.Z), geometry.Point3D(
            handle_3.X, handle_3.Y, handle_3.Z), [("wid", HandleDirection.x_dir)], HandleDirection.x_dir, False))
        handle_4 = geometry.Point3D(0 - (get_info[7] - get_info[0]) / 2,
                                    get_info[1], get_info[4] + get_info[2] + get_info[12])
        self.handle_list.append(HandleProperties("widup", geometry.Point3D(handle_4.X + get_info[7], handle_4.Y, handle_4.Z), geometry.Point3D(
            handle_4.X, handle_4.Y, handle_4.Z), [("widup", HandleDirection.x_dir)], HandleDirection.x_dir, False))
        handle_5 = geometry.Point3D(get_info[0] / 2, get_info[1],
                                    get_info[4] + get_info[2] - get_info[2] / 4)
        self.handle_list.append(HandleProperties("heup", geometry.Point3D(handle_5.X, handle_5.Y, handle_5.Z + get_info[8]), geometry.Point3D(
            handle_5.X, handle_5.Y, handle_5.Z), [("heup", HandleDirection.z_dir)], HandleDirection.z_dir, False))
        handle_6 = geometry.Point3D(get_info[0] / 2, get_info[1],
                                    get_info[4] + get_info[2] + get_info[8])
        self.handle_list.append(HandleProperties("plhe", geometry.Point3D(handle_6.X, handle_6.Y, handle_6.Z + get_info[10]), geometry.Point3D(
            handle_6.X, handle_6.Y, handle_6.Z), [("plhe", HandleDirection.z_dir)], HandleDirection.z_dir, False))
        handle_7 = geometry.Point3D(get_info[0] / 2, get_info[1], 0)
        self.handle_list.append(HandleProperties("he", geometry.Point3D(handle_7.X, handle_7.Y, handle_7.Z + get_info[2]), geometry.Point3D(
            handle_7.X, handle_7.Y, handle_7.Z), [("he", HandleDirection.z_dir)], HandleDirection.z_dir, False))
        handle_8 = geometry.Point3D(get_info[0] / 2 - get_info[3] / 2,
                                    get_info[1], get_info[4] / 2 + get_info[2])
        self.handle_list.append(HandleProperties("middlewid", geometry.Point3D(handle_8.X + get_info[3], handle_8.Y, handle_8.Z), geometry.Point3D(
            handle_8.X, handle_8.Y, handle_8.Z), [("middlewid", HandleDirection.x_dir)], HandleDirection.x_dir, False))

    def get(self, build_ele):
        wid = build_ele.wid.value
        len = build_ele.len.value
        he = build_ele.he.value
        middlewid = build_ele.middlewid.value
        middlehe = build_ele.middlehe.value
        sectiont = build_ele.sectiont.value
        rad = build_ele.rad.value
        widup = build_ele.widup.value
        heup = build_ele.heup.value
        plsp = build_ele.plsp.value
        plhe = build_ele.plhe.value
        color = build_ele.color.value
        sectionupb = build_ele.sectionupb.value
        return [wid, len, he, middlewid, middlehe, sectiont, rad, widup, heup, plsp, plhe, color, sectionupb]
