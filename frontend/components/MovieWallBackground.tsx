"use client";

import { useEffect, useState } from "react";

// 安全海报池 - 硬编码有效URL，绝无死链
const SAFE_POSTERS = [
  "https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
  "https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg",
  "https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg",
  "https://image.tmdb.org/t/p/w500/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg",
  "https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg",
  "https://image.tmdb.org/t/p/w500/8Z8dptEQvKvwX2nK0AtsLpE7lJ2.jpg",
  "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
  "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
  "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
  "https://image.tmdb.org/t/p/w500/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg",
];

// 备用的彩色渐变兜底
const FALLBACK_BG = [
  "from-blue-900/80 to-purple-900/80",
  "from-red-900/80 to-orange-900/80",
  "from-purple-900/80 to-pink-900/80",
  "from-cyan-900/80 to-blue-900/80",
  "from-orange-900/80 to-yellow-900/80",
  "from-yellow-900/80 to-red-900/80",
  "from-pink-900/80 to-purple-900/80",
  "from-emerald-900/80 to-cyan-900/80",
  "from-violet-900/80 to-blue-900/80",
  "from-amber-900/80 to-orange-900/80",
];

interface MovieWallBackgroundProps {
  darkness?: "normal" | "heavy";
}

export default function MovieWallBackground({ darkness = "normal" }: MovieWallBackgroundProps) {
  const [mounted, setMounted] = useState(false);
  const [duplicatedPosters, setDuplicatedPosters] = useState<string[]>([]);

  useEffect(() => {
    // 将10张海报复制12次，变成120张填满容器
    const posters: string[] = [];
    for (let i = 0; i < 12; i++) {
      posters.push(...SAFE_POSTERS);
    }
    // 打乱顺序
    const shuffled = posters.sort(() => Math.random() - 0.5);
    setDuplicatedPosters(shuffled);
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="fixed inset-0 bg-[#0a0a0a] z-0" />;
  }

  // heavy模式下添加额外的深色遮罩
  const heavyOverlay = darkness === "heavy" ? (
    <div className="absolute inset-0 bg-black/60 z-[5]" />
  ) : null;

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {/* 超大倾斜容器 - 160vw x 160vh 确保填满 */}
      <div 
        className="absolute saturate-150 contrast-125 animate-slow-drift"
        style={{
          width: '160vw',
          height: '160vh',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%) rotate(-12deg)',
          filter: 'blur(1px)',
          display: 'grid',
          gridTemplateColumns: 'repeat(15, 1fr)',
          gridAutoRows: '1fr',
          gap: '4px',
          padding: '4px',
        }}
      >
        {duplicatedPosters.map((url, index) => (
          <div
            key={`poster-${index}-${url}`}
            className={`w-28 sm:w-32 md:w-36 aspect-[2/3] rounded-sm bg-gradient-to-br ${FALLBACK_BG[index % FALLBACK_BG.length]}`}
            style={{
              opacity: 0.5 + (Math.sin(index * 0.4) * 0.1),
            }}
          >
            <img
              src={url}
              alt=""
              className="w-full h-full object-cover rounded-sm"
              loading="eager"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = 'none';
              }}
            />
          </div>
        ))}
      </div>

      {/* 舞台聚光灯式暗角 */}
      <div 
        className="absolute inset-0 z-10 pointer-events-none"
        style={{
          background: 'radial-gradient(circle at center, transparent 15%, rgba(10,10,15,0.4) 40%, rgba(10,10,15,0.85) 65%, #0a0a0f 100%)',
        }}
      />
      
      {/* 顶部黑边 */}
      <div 
        className="absolute top-0 left-0 right-0 h-32 z-11 pointer-events-none"
        style={{
          background: 'linear-gradient(to bottom, #0a0a0f 0%, rgba(10,10,15,0.95) 50%, transparent 100%)',
        }}
      />
      
      {/* 底部黑边 */}
      <div 
        className="absolute bottom-0 left-0 right-0 h-40 z-11 pointer-events-none"
        style={{
          background: 'linear-gradient(to top, #0a0a0f 0%, rgba(10,10,15,0.95) 50%, transparent 100%)',
        }}
      />
      
      {/* 顶部红色光晕 */}
      <div 
        className="absolute top-0 left-0 right-0 h-48 z-12 pointer-events-none"
        style={{
          background: 'linear-gradient(to bottom, rgba(220,38,38,0.1) 0%, transparent 100%)',
        }}
      />

      {/* heavy模式额外遮罩 */}
      {heavyOverlay}
    </div>
  );
}