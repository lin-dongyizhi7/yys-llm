/*
 * @Author: 凛冬已至 2985956026@qq.com
 * @Date: 2025-08-25 10:12:38
 * @LastEditors: 凛冬已至 2985956026@qq.com
 * @LastEditTime: 2025-08-25 10:30:11
 * @FilePath: \my-llm\shudo\src\components\Timer.tsx
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
import React, { useState, useEffect, useCallback } from 'react';
import './Timer.css';

interface TimerProps {
  isActive: boolean;
  onTimeUpdate?: (time: number) => void;
}

const Timer: React.FC<TimerProps> = ({ isActive, onTimeUpdate }) => {
  const [time, setTime] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    if (isActive && !isPaused) {
      interval = setInterval(() => {
        setTime(prevTime => {
          const newTime = prevTime + 1;
          onTimeUpdate?.(newTime);
          return newTime;
        });
      }, 1000);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [isActive, isPaused, onTimeUpdate]);

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handlePauseResume = () => {
    setIsPaused(!isPaused);
  };

  if (!isActive) return null;

  return (
    <div className="timer">
      <div className="timer-display">
        <span className="timer-label">时间:</span>
        <span className="timer-value">{formatTime(time)}</span>
        <button
          className={`timer-button ${isPaused ? 'resume' : 'pause'}`}
          onClick={handlePauseResume}
        >
          {isPaused ? '▶️ 继续' : '⏸️ 暂停'}
        </button>
      </div>
    </div>
  );
};

export default Timer;
