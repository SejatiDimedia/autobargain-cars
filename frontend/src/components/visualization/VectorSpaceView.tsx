import { useState, useMemo, useRef, useEffect, useCallback } from 'react'
import {
  Database,
  Sparkles,
  Info,
  RotateCw,
  Play,
  Pause,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Compass,
} from 'lucide-react'
import { useTsnePlot } from '../../hooks/useStats'
import { TsnePoint } from '../../types/api'

interface Point3D {
  orig: TsnePoint
  x: number // normalized -150 to 150
  y: number
  z: number
  // projected
  rotX: number
  rotY: number
  rotZ: number
  screenX: number
  screenY: number
  radius: number
  opacity: number
}

interface Edge3D {
  from: [number, number, number]
  to: [number, number, number]
}

export function VectorSpaceView() {
  const { data: plotData, isLoading } = useTsnePlot(500)
  const [selectedBrand, setSelectedBrand] = useState<string>('all')
  const [hoveredPoint, setHoveredPoint] = useState<TsnePoint | null>(null)
  const [isAutoRotate, setIsAutoRotate] = useState<boolean>(true)
  const [zoom, setZoom] = useState<number>(1.0)

  // Camera angles in radians
  const [pitch, setPitch] = useState<number>(0.35) // ~20 deg elevation
  const [yaw, setYaw] = useState<number>(0.75) // ~43 deg azimuth

  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const isDraggingRef = useRef<boolean>(false)
  const lastMousePosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 })
  const hoveredPointRef = useRef<TsnePoint | null>(null)
  hoveredPointRef.current = hoveredPoint

  const points = plotData?.points || []

  // Normalization bounds for 3D coordinates
  const bounds = useMemo(() => {
    if (points.length === 0) return { minX: 0, maxX: 1, minY: 0, maxY: 1, minZ: 0, maxZ: 1 }
    let minX = Infinity, maxX = -Infinity
    let minY = Infinity, maxY = -Infinity
    let minZ = Infinity, maxZ = -Infinity
    points.forEach((p) => {
      if (p.x < minX) minX = p.x
      if (p.x > maxX) maxX = p.x
      if (p.y < minY) minY = p.y
      if (p.y > maxY) maxY = p.y
      if (p.z < minZ) minZ = p.z
      if (p.z > maxZ) maxZ = p.z
    })
    return { minX, maxX, minY, maxY, minZ, maxZ }
  }, [points])

  const filteredPoints = useMemo(() => {
    if (selectedBrand === 'all') return points
    return points.filter((p) => p.brand === selectedBrand)
  }, [points, selectedBrand])

  // Map points to centered 3D space [-130, 130]
  const normalizedPoints = useMemo(() => {
    const spanX = (bounds.maxX - bounds.minX) || 1
    const spanY = (bounds.maxY - bounds.minY) || 1
    const spanZ = (bounds.maxZ - bounds.minZ) || 1

    return filteredPoints.map((p) => {
      const nx = ((p.x - bounds.minX) / spanX - 0.5) * 260
      // Invert Y for standard 3D cartesian coordinates
      const ny = -((p.y - bounds.minY) / spanY - 0.5) * 260
      const nz = ((p.z - bounds.minZ) / spanZ - 0.5) * 260

      return {
        orig: p,
        x: nx,
        y: ny,
        z: nz,
      }
    })
  }, [filteredPoints, bounds])

  // Reset to default isometric camera
  const handleResetCamera = useCallback(() => {
    setPitch(0.35)
    setYaw(0.75)
    setZoom(1.0)
  }, [])

  // Presets
  const setPresetView = (type: 'iso' | 'top' | 'front' | 'side') => {
    if (type === 'iso') {
      setPitch(0.35)
      setYaw(0.75)
    } else if (type === 'top') {
      setPitch(Math.PI / 2 - 0.05)
      setYaw(0)
    } else if (type === 'front') {
      setPitch(0)
      setYaw(0)
    } else if (type === 'side') {
      setPitch(0)
      setYaw(Math.PI / 2)
    }
  }

  // Animation Loop & Canvas Rendering
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animationFrameId: number

    // Render Function
    const render = () => {
      // Auto-rotation when enabled and user is not dragging
      if (isAutoRotate && !isDraggingRef.current) {
        setYaw((prev) => (prev + 0.005) % (Math.PI * 2))
      }

      const rect = canvas.getBoundingClientRect()
      const dpr = window.devicePixelRatio || 1
      const width = rect.width
      const height = rect.height

      if (canvas.width !== width * dpr || canvas.height !== height * dpr) {
        canvas.width = width * dpr
        canvas.height = height * dpr
      }

      ctx.save()
      ctx.scale(dpr, dpr)
      ctx.clearRect(0, 0, width, height)

      const centerX = width / 2
      const centerY = height / 2 + 10
      const cameraDist = 550
      const fov = 480 * zoom

      // 3D Projection math
      const cosY = Math.cos(yaw)
      const sinY = Math.sin(yaw)
      const cosP = Math.cos(pitch)
      const sinP = Math.sin(pitch)

      const project = (x: number, y: number, z: number) => {
        // Rotate around Y axis (yaw)
        const x1 = x * cosY - z * sinY
        const z1 = x * sinY + z * cosY

        // Rotate around X axis (pitch)
        const y2 = y * cosP - z1 * sinP
        const z2 = y * sinP + z1 * cosP

        const scale = fov / (cameraDist + z2)
        const sx = centerX + x1 * scale
        const sy = centerY + y2 * scale

        return {
          sx,
          sy,
          zDepth: z2,
          scale,
        }
      }

      // 1. Draw 3D Bounding Cube Box (Wireframe cage)
      const S = 140 // Half size of cube
      const cubeCorners: [number, number, number][] = [
        [-S, -S, -S],
        [S, -S, -S],
        [S, -S, S],
        [-S, -S, S],
        [-S, S, -S],
        [S, S, -S],
        [S, S, S],
        [-S, S, S],
      ]

      const projectedCorners = cubeCorners.map(([cx, cy, cz]) => project(cx, cy, cz))

      // 12 edges of cube
      const edges: [number, number][] = [
        // Bottom plane
        [0, 1], [1, 2], [2, 3], [3, 0],
        // Top plane
        [4, 5], [5, 6], [6, 7], [7, 4],
        // Vertical pillars
        [0, 4], [1, 5], [2, 6], [3, 7],
      ]

      // Draw subtle floor grid (y = -S, bottom plane)
      ctx.strokeStyle = '#f1f5f9'
      ctx.lineWidth = 1
      const gridSteps = 4
      for (let i = 1; i < gridSteps; i++) {
        const frac = -S + (2 * S * i) / gridSteps
        const pA = project(frac, -S, -S)
        const pB = project(frac, -S, S)
        ctx.beginPath()
        ctx.moveTo(pA.sx, pA.sy)
        ctx.lineTo(pB.sx, pB.sy)
        ctx.stroke()

        const pC = project(-S, -S, frac)
        const pD = project(S, -S, frac)
        ctx.beginPath()
        ctx.moveTo(pC.sx, pC.sy)
        ctx.lineTo(pD.sx, pD.sy)
        ctx.stroke()
      }

      // Draw cube edges with depth styling
      ctx.strokeStyle = '#e2e8f0'
      ctx.setLineDash([4, 4])
      ctx.lineWidth = 1
      edges.forEach(([iA, iB]) => {
        const pA = projectedCorners[iA]
        const pB = projectedCorners[iB]
        ctx.beginPath()
        ctx.moveTo(pA.sx, pA.sy)
        ctx.lineTo(pB.sx, pB.sy)
        ctx.stroke()
      })
      ctx.setLineDash([])

      // 2. Draw 3D Cartesian Coordinate Axes from Center (0, 0, 0)
      const origin = project(0, -S, 0) // Floor center
      const axisLen = 65

      const xAxis = project(axisLen, -S, 0)
      const yAxis = project(0, -S + axisLen, 0)
      const zAxis = project(0, -S, axisLen)

      // X Axis (Red)
      ctx.strokeStyle = '#ef4444'
      ctx.lineWidth = 1.8
      ctx.beginPath()
      ctx.moveTo(origin.sx, origin.sy)
      ctx.lineTo(xAxis.sx, xAxis.sy)
      ctx.stroke()

      // Y Axis (Green / Height)
      ctx.strokeStyle = '#10b981'
      ctx.lineWidth = 1.8
      ctx.beginPath()
      ctx.moveTo(origin.sx, origin.sy)
      ctx.lineTo(yAxis.sx, yAxis.sy)
      ctx.stroke()

      // Z Axis (Blue / Depth)
      ctx.strokeStyle = '#3b82f6'
      ctx.lineWidth = 1.8
      ctx.beginPath()
      ctx.moveTo(origin.sx, origin.sy)
      ctx.lineTo(zAxis.sx, zAxis.sy)
      ctx.stroke()

      // Small Axis Labels
      ctx.font = '9px ui-monospace, SFMono-Regular, Menlo, monospace'
      ctx.fillStyle = '#ef4444'
      ctx.fillText('X (t-SNE 1)', xAxis.sx + 4, xAxis.sy)
      ctx.fillStyle = '#10b981'
      ctx.fillText('Y (t-SNE 2)', yAxis.sx + 4, yAxis.sy)
      ctx.fillStyle = '#3b82f6'
      ctx.fillText('Z (t-SNE 3)', zAxis.sx + 4, zAxis.sy)

      // 3. Project and Sort All Data Points (Painter's Algorithm by Depth)
      const projectedPoints: Point3D[] = normalizedPoints.map((item) => {
        const { sx, sy, zDepth, scale } = project(item.x, item.y, item.z)
        // Depth-dependent radius and opacity
        const baseR = 5.0
        const radius = Math.max(2.5, Math.min(10.5, baseR * scale * 1.15))
        const depthNorm = (zDepth + 200) / 400 // 0 (far) to 1 (near)
        const opacity = Math.max(0.45, Math.min(1.0, 0.45 + depthNorm * 0.55))

        return {
          orig: item.orig,
          x: item.x,
          y: item.y,
          z: item.z,
          rotX: 0,
          rotY: 0,
          rotZ: zDepth,
          screenX: sx,
          screenY: sy,
          radius,
          opacity,
        }
      })

      // Sort points from furthest to nearest
      projectedPoints.sort((a, b) => a.rotZ - b.rotZ)

      // Draw shadow drops on floor for 3D grounding
      projectedPoints.forEach((p) => {
        const floorPt = project(p.x, -S, p.z)
        ctx.beginPath()
        ctx.ellipse(floorPt.sx, floorPt.sy, p.radius * 0.7, p.radius * 0.35, 0, 0, Math.PI * 2)
        ctx.fillStyle = 'rgba(15, 23, 42, 0.04)'
        ctx.fill()
      })

      // Draw 3D Points with volumetric radial gradients
      const currentHovered = hoveredPointRef.current

      projectedPoints.forEach((p) => {
        const isHovered = currentHovered === p.orig
        const ptRadius = isHovered ? p.radius * 1.6 : p.radius

        // If hovered, draw a vertical stem line to floor grid
        if (isHovered) {
          const floorPt = project(p.x, -S, p.z)
          ctx.strokeStyle = 'rgba(255, 105, 0, 0.5)'
          ctx.lineWidth = 1.2
          ctx.setLineDash([2, 2])
          ctx.beginPath()
          ctx.moveTo(p.screenX, p.screenY)
          ctx.lineTo(floorPt.sx, floorPt.sy)
          ctx.stroke()
          ctx.setLineDash([])

          // Floor target ring
          ctx.strokeStyle = '#ff6900'
          ctx.lineWidth = 1.5
          ctx.beginPath()
          ctx.ellipse(floorPt.sx, floorPt.sy, 6, 3, 0, 0, Math.PI * 2)
          ctx.stroke()

          // 3D Pulse Halo
          ctx.beginPath()
          ctx.arc(p.screenX, p.screenY, ptRadius + 4, 0, Math.PI * 2)
          ctx.strokeStyle = '#ff6900'
          ctx.lineWidth = 2
          ctx.stroke()
        }

        // 3D Spherical Radial Gradient
        const grad = ctx.createRadialGradient(
          p.screenX - ptRadius * 0.3,
          p.screenY - ptRadius * 0.3,
          ptRadius * 0.1,
          p.screenX,
          p.screenY,
          ptRadius
        )

        // Sphere highlight
        grad.addColorStop(0, '#ffffff')
        grad.addColorStop(0.35, p.orig.color)
        grad.addColorStop(1, isHovered ? '#0f172a' : p.orig.color)

        ctx.beginPath()
        ctx.arc(p.screenX, p.screenY, ptRadius, 0, Math.PI * 2)
        ctx.fillStyle = grad
        ctx.globalAlpha = isHovered ? 1.0 : p.opacity
        ctx.fill()

        // Subtle dark outline
        ctx.strokeStyle = isHovered ? '#0f172a' : 'rgba(255, 255, 255, 0.85)'
        ctx.lineWidth = isHovered ? 1.5 : 0.75
        ctx.stroke()
        ctx.globalAlpha = 1.0
      })

      ctx.restore()
    }

    render()
    animationFrameId = requestAnimationFrame(render)

    return () => {
      cancelAnimationFrame(animationFrameId)
    }
  }, [normalizedPoints, pitch, yaw, zoom, isAutoRotate])

  // Mouse & Drag Orbit Handlers
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    isDraggingRef.current = true
    lastMousePosRef.current = { x: e.clientX, y: e.clientY }
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    if (isDraggingRef.current) {
      const deltaX = e.clientX - lastMousePosRef.current.x
      const deltaY = e.clientY - lastMousePosRef.current.y
      lastMousePosRef.current = { x: e.clientX, y: e.clientY }

      // Adjust yaw & pitch
      setYaw((prev) => prev + deltaX * 0.008)
      setPitch((prev) => {
        const next = prev - deltaY * 0.008
        // Clamp pitch to avoid gimbal flipping
        return Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, next))
      })
      return
    }

    // Raycast / Proximity detection for Hover
    const rect = canvas.getBoundingClientRect()
    const mouseX = e.clientX - rect.left
    const mouseY = e.clientY - rect.top

    const centerX = rect.width / 2
    const centerY = rect.height / 2 + 10
    const cameraDist = 550
    const fov = 480 * zoom

    const cosY = Math.cos(yaw)
    const sinY = Math.sin(yaw)
    const cosP = Math.cos(pitch)
    const sinP = Math.sin(pitch)

    let closest: TsnePoint | null = null
    let minDistanceSq = 14 * 14 // 14px hover radius threshold

    normalizedPoints.forEach((item) => {
      const x1 = item.x * cosY - item.z * sinY
      const z1 = item.x * sinY + item.z * cosY
      const y2 = item.y * cosP - z1 * sinP
      const z2 = item.y * sinP + z1 * cosP

      const scale = fov / (cameraDist + z2)
      const sx = centerX + x1 * scale
      const sy = centerY + y2 * scale

      const dx = sx - mouseX
      const dy = sy - mouseY
      const distSq = dx * dx + dy * dy

      if (distSq < minDistanceSq) {
        minDistanceSq = distSq
        closest = item.orig
      }
    })

    if (closest !== hoveredPoint) {
      setHoveredPoint(closest)
    }
  }

  const handleMouseUp = () => {
    isDraggingRef.current = false
  }

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault()
    setZoom((prev) => Math.max(0.55, Math.min(2.5, prev - e.deltaY * 0.0015)))
  }

  return (
    <div className="space-y-4">
      {/* Header Bar */}
      <div className="flex flex-col md:flex-row gap-3 items-start md:items-center justify-between p-4 bg-white rounded-2xl border border-surface-border shadow-subtle">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-purple-50 text-purple-700 border border-purple-100">
            <Database className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-slate-900">
                ChromaDB 3D Embedding Vector Space
              </h3>
              <span className="text-[10px] px-2 py-0.5 rounded-md font-mono bg-purple-100 text-purple-800 font-bold uppercase tracking-wider">
                True 3D View
              </span>
            </div>
            <p className="text-xs text-slate-600 mt-0.5">
              Proyeksi t-SNE 3D interaktif dari kemiripan semantik mobil bekas pada Vector Database.
            </p>
          </div>
        </div>

        {/* Brand Legend Pills */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <button
            onClick={() => setSelectedBrand('all')}
            className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all focus-visible:ring-2 focus-visible:ring-brand-orange ${
              selectedBrand === 'all'
                ? 'bg-slate-900 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            Semua ({points.length})
          </button>
          {plotData?.brands?.slice(0, 7).map((brand, i) => {
            const color = plotData.brand_colors[i] || '#888'
            const isSelected = selectedBrand === brand
            return (
              <button
                key={brand}
                onClick={() => setSelectedBrand(brand)}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all border focus-visible:ring-2 focus-visible:ring-brand-orange ${
                  isSelected
                    ? 'border-slate-800 bg-white text-slate-900 shadow-sm'
                    : 'border-transparent bg-slate-50 text-slate-700 hover:bg-slate-100'
                }`}
              >
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                <span>{brand}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Main Canvas Area */}
      <div className="relative bg-white rounded-2xl border border-surface-border shadow-subtle p-4 flex flex-col items-center justify-center min-h-[500px] overflow-hidden select-none">
        {/* Floating 3D Control Toolbar */}
        <div className="absolute top-4 right-4 z-10 flex items-center gap-1.5 p-1.5 rounded-xl bg-white/90 backdrop-blur-md border border-surface-border shadow-sm">
          <button
            onClick={() => setIsAutoRotate(!isAutoRotate)}
            title={isAutoRotate ? 'Jeda Putaran Otomatis' : 'Putar Otomatis 3D'}
            className={`p-1.5 rounded-lg text-xs font-medium transition-all ${
              isAutoRotate
                ? 'bg-brand-orange text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            {isAutoRotate ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
          </button>

          <div className="h-4 w-px bg-slate-200 mx-0.5" />

          <button
            onClick={() => setZoom((z) => Math.min(2.5, z + 0.15))}
            title="Perbesar (Zoom In)"
            className="p-1.5 rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition-all"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setZoom((z) => Math.max(0.55, z - 0.15))}
            title="Perkecil (Zoom Out)"
            className="p-1.5 rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition-all"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>

          <div className="h-4 w-px bg-slate-200 mx-0.5" />

          {/* Perspective Preset Buttons */}
          <button
            onClick={() => setPresetView('iso')}
            title="Sudut Isometrik 3D"
            className="px-2 py-1 rounded-lg text-[11px] font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-all"
          >
            3D Iso
          </button>
          <button
            onClick={() => setPresetView('top')}
            title="Tampak Atas (Top View)"
            className="px-2 py-1 rounded-lg text-[11px] font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-all"
          >
            Atas
          </button>
          <button
            onClick={() => setPresetView('front')}
            title="Tampak Depan (Front View)"
            className="px-2 py-1 rounded-lg text-[11px] font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition-all"
          >
            Depan
          </button>

          <div className="h-4 w-px bg-slate-200 mx-0.5" />

          <button
            onClick={handleResetCamera}
            title="Reset Sudut Kamera"
            className="p-1.5 rounded-lg bg-slate-100 text-slate-700 hover:bg-slate-200 transition-all"
          >
            <RotateCw className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Floating Instruction Badge */}
        <div className="absolute top-4 left-4 z-10 pointer-events-none flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/80 backdrop-blur-sm border border-slate-200/80 text-[11px] text-slate-600 shadow-xs">
          <Compass className="w-3.5 h-3.5 text-brand-orange animate-spin" style={{ animationDuration: '8s' }} />
          <span>Klik & geser untuk memutar 3D • Scroll untuk zoom</span>
        </div>

        {isLoading ? (
          <div className="flex flex-col items-center gap-2 text-slate-500 text-xs py-20">
            <Sparkles className="w-6 h-6 animate-spin text-brand-orange" />
            <span>Menghitung proyeksi t-SNE 3D dari ChromaDB embeddings...</span>
          </div>
        ) : points.length === 0 ? (
          <div className="text-slate-500 text-xs py-20">
            Database belum memiliki titik data embedding. Jalankan pemindaian terlebih dahulu.
          </div>
        ) : (
          <div className="w-full flex flex-col items-center">
            {/* Interactive HTML5 3D Canvas */}
            <canvas
              ref={canvasRef}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              onWheel={handleWheel}
              className="w-full h-[400px] cursor-grab active:cursor-grabbing touch-none"
              style={{ width: '100%', height: '400px' }}
            />

            {/* Hovered Point Card Banner / HUD */}
            <div className="w-full max-w-2xl mt-2 p-3.5 rounded-xl bg-surface-subtle border border-surface-border flex items-start gap-3 text-left text-xs min-h-[64px] transition-all">
              <Info className="w-4 h-4 text-brand-orange shrink-0 mt-0.5" />
              {hoveredPoint ? (
                <div className="w-full">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: hoveredPoint.color }} />
                      <span className="font-bold text-slate-900">{hoveredPoint.brand}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-200/80 text-slate-700 font-mono tabular-nums">
                        Embedding #{points.indexOf(hoveredPoint) + 1}
                      </span>
                    </div>

                    {/* Exact 3D Coordinates */}
                    <div className="flex items-center gap-2 text-[10px] font-mono tabular-nums text-slate-600 bg-white px-2 py-0.5 rounded border border-slate-200">
                      <span>X: {hoveredPoint.x.toFixed(1)}</span>
                      <span className="text-slate-300">|</span>
                      <span>Y: {hoveredPoint.y.toFixed(1)}</span>
                      <span className="text-slate-300">|</span>
                      <span>Z: {hoveredPoint.z.toFixed(1)}</span>
                    </div>
                  </div>

                  <p className="text-[11px] text-slate-700 mt-1 line-clamp-2 leading-relaxed">
                    {hoveredPoint.description}
                  </p>
                </div>
              ) : (
                <div className="flex items-center justify-between w-full">
                  <p className="text-[11px] text-slate-500 italic">
                    Arahkan kursor atau drag bola 3D untuk melihat koordinat semantik dokumen mobil yang terindeks di ChromaDB.
                  </p>
                  <span className="text-[10px] font-mono tabular-nums text-slate-500 shrink-0">
                    Total: {filteredPoints.length} Vektor
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
