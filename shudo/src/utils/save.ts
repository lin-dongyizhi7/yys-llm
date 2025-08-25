export interface SaveOptions {
  difficultyName?: string | null;
  directoryName?: string; // 未使用，仅保留接口一致性
}

function formatTwo(n: number): string {
  return n < 10 ? `0${n}` : `${n}`;
}

function buildFilename(difficultyName?: string | null): string {
  const now = new Date();
  const yyyy = now.getFullYear();
  const MM = formatTwo(now.getMonth() + 1);
  const dd = formatTwo(now.getDate());
  const hh = formatTwo(now.getHours());
  const mm = formatTwo(now.getMinutes());
  const ss = formatTwo(now.getSeconds());
  const diff = (difficultyName || '未知').replace(/\s+/g, '');
  return `${yyyy}${MM}${dd}-${hh}${mm}${ss}-${diff}.json`;
}

/**
 * 将数独棋盘保存为JSON文件，格式为 { data: number[][] }
 * 文件名：YYYYMMDD-HHMMSS-难度.json
 * 优先使用 File System Access API；否则回退为浏览器下载
 */
export async function saveSudokuToJson(board: number[][], options?: SaveOptions): Promise<void> {
  const filename = buildFilename(options?.difficultyName);
  const payload = { data: board };
  const json = JSON.stringify(payload, null, 2);
  const blob = new Blob([json], { type: 'application/json;charset=utf-8' });

  // 尝试使用 File System Access API（仅在部分浏览器可用，需HTTPS/localhost）
  const nav: any = typeof window !== 'undefined' ? (window as any).navigator : null;
  const hasFilePicker = typeof (window as any).showSaveFilePicker === 'function';

  try {
    if (hasFilePicker) {
      const handle = await (window as any).showSaveFilePicker({
        suggestedName: filename,
        types: [
          {
            description: 'JSON Files',
            accept: { 'application/json': ['.json'] },
          },
        ],
      });
      const writable = await handle.createWritable();
      await writable.write(blob);
      await writable.close();
      return;
    }
  } catch (err) {
    // 如果用户取消或API不可用，继续走下载回退
    // console.warn('File System Access API 不可用或用户取消，使用下载回退', err);
  }

  // 回退：创建一个下载链接
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
