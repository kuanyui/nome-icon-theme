import { SVG, Container, Rect, Element, registerWindow, List } from '@svgdotjs/svg.js'
import { promises as fs } from 'fs'
import path from 'path'
const { createSVGWindow } = await import('svgdom')

const window = createSVGWindow()
const document = window.document
registerWindow(window, document)

interface CropDimension {
    x: number
    y: number
    width: number
    height: number
}

async function cropSvg(svgFile: string, outputDir: string): Promise<void> {
    const svgFileName = path.basename(svgFile, '.svg')
    const svgFileContent = await fs.readFile(svgFile, 'utf-8')

    const dummyDom = SVG(document.documentElement)
    dummyDom.clear()
    dummyDom.svg(svgFileContent)
    const dom = dummyDom.findOne('svg')!
    // console.log(dom.svg())
    const baseplates = dom.find('g').filter(element =>
        element.attr('inkscape:label') === 'baseplate'
    )

    for (const baseplate of baseplates) {
        let currentIconName = svgFileName

        const baseplateParent = baseplate.parent() as Container
        if (baseplateParent && baseplateParent.type === 'g') {
            const parentLabel = baseplateParent.attr('inkscape:label')
            if (parentLabel && parentLabel !== '') {
                currentIconName = parentLabel
            }
        }
        const rects = baseplate.find('rect') as List<Rect>

        for (const rect of rects) {
            const sizeLabel = rect.attr('inkscape:label')
            if (!['16x16', '22x22', '24x24', '32x32', '48x48'].includes(sizeLabel)) {
                continue
            }
            // console.log(rect)

            const bbox = rect.bbox()   // original
            const rbox = rect.rbox()   // transformed
            const t = baseplateParent.transform()
            // const obox = {
            //     x: +rect.x(),
            //     y: +rect.y(),
            //     width: +rect.width(),
            //     height: +rect.height()
            // }
            const cropBox: CropDimension = {
                x: bbox.x + (t.translateX || 0),
                y: bbox.y + (t.translateY || 0),
                width: bbox.width,
                height: bbox.height
            }
            // console.log(`${currentIconName} ${sizeLabel} (orig) ==> \t ${~~obox.x},\t ${~~obox.y},\t ${~~obox.width},\t ${~~obox.height}`)
            console.log(`${currentIconName} ${sizeLabel} (bbox) ==> \t ${~~bbox.x},\t ${~~bbox.y},\t ${~~bbox.width},\t ${~~bbox.height}`)
            console.log(`${currentIconName} ${sizeLabel} (tran) ==> \t ${t.translateX},\t ${t.translateY}`)
            console.log(`${currentIconName} ${sizeLabel} (rbox) ==> \t ${~~rbox.x},\t ${~~rbox.y},\t ${~~rbox.width},\t ${~~rbox.height}`)
            console.log('')

            await createSvgFile(cropBox, svgFileContent, outputDir, currentIconName)
        }
    }
}

async function createSvgFile(
    dimensions: CropDimension,
    originalSvg: string,
    outputDir: string,
    iconName: string
): Promise<void> {
    const dummyDom = SVG(document.documentElement)
    dummyDom.svg(originalSvg)
    const dom = dummyDom.findOne('svg')!
    dom.attr('viewBox', `${dimensions.x} ${dimensions.y} ${dimensions.width} ${dimensions.height}`)
    dom.attr('width', dimensions.width)
    dom.attr('height', dimensions.height)

    await fs.mkdir(outputDir, { recursive: true })

    const outputFile = path.join(outputDir, `${iconName}_${dimensions.width}.svg`)
    let svgString = dom.svg()

    // if (svgString.startsWith('<?xml')) {
    //     svgString = svgString.substring(svgString.indexOf('?>') + 2)
    // }

    await fs.writeFile(outputFile, svgString, 'utf-8')
}

export function main() {
    // cropSvg('../thirdparty/gnome-icon-theme-3.9.5/src/clocks.svg', 'dist/gnome_output')
    cropSvg('../thirdparty/gnome-icon-theme-3.9.5/src/displays.svg', 'dist/gnome_output')
    // cropSvg('../thirdparty/gnome-icon-theme-3.9.5/src/accessories-calculator.svg', 'dist/gnome_output')
}

main()

export { }