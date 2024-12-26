import inkex

def dbg(obj):
    for attr in dir(obj):
        if not attr.startswith('__'):
            inkex.utils.debug(f"{attr}: {getattr(obj, attr)}")


class DeleteOutOfPageObjects(inkex.extensions.EffectExtension):
    def effect(self):
        svg = self.document.getroot()
        page_width = svg.unittouu(svg.get('width', '0'))
        page_height = svg.unittouu(svg.get('height', '0'))
        dbg(vars(self))
        dbg([svg, page_width, page_height])
        for element in svg.xpath('//svg:*', namespaces=inkex.NSS):
            bbox = self.compute_transformed_bbox(element)
            if bbox is not None:
                x_min, y_min, x_max, y_max = bbox
                if x_max < 0 or y_max < 0 or x_min > page_width or y_min > page_height:
                    element.getparent().remove(element)

    def compute_transformed_bbox(self, element):
        try:
            dbg(vars(self.svg))
            bbox = element.bounding_box()
            return bbox.left, bbox.top, bbox.right, bbox.bottom
        except Exception:
            return None

if __name__ == '__main__':
    DeleteOutOfPageObjects().run()
