import SparkMD5 from 'spark-md5';

export interface Chunk {
    blob: Blob;
    md5: string;
}

// 计算单个分片的 MD5
const computeChunkMD5 = (chunk: Blob): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const spark = new SparkMD5.ArrayBuffer();
            spark.append(e.target?.result as ArrayBuffer);
            resolve(spark.end());
        };
        reader.onerror = () => reject(new Error('分片 MD5 计算失败'));
        reader.readAsArrayBuffer(chunk);
    });
};

// 并发计算所有分片并返回 Promise
export const calculateChunkMD5 = (file: File, chunkSize: number, first_chunk_index: number = 0): Promise<Chunk[]> => {
    const totalChunks = Math.ceil(file.size / chunkSize);
    const tasks: Promise<Chunk>[] = [];

    for (let i = first_chunk_index; i < totalChunks; i++) {
        const start = i * chunkSize;
        const end = Math.min(start + chunkSize, file.size);
        const chunk = file.slice(start, end);

        tasks.push(
            computeChunkMD5(chunk).then(md5 => ({
                blob: chunk,
                md5: md5
            }))
        );
    }

    return Promise.all(tasks);
};

export async function calculateSHA256(file: Blob): Promise<string> {
    const buffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
}