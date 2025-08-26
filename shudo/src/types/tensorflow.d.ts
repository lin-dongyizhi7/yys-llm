declare module '@tensorflow/tfjs' {
  export interface Tensor {
    shape: number[];
    array(): Promise<any>;
    flatten(): Tensor;
    dispose(): void;
  }

  export interface LayersModel {
    predict(input: Tensor): Tensor;
  }

  export const browser: {
    fromPixels(imageData: ImageData, channels?: number): Tensor;
  };

  export function loadLayersModel(path: string): Promise<LayersModel>;
  export function div(a: Tensor, b: number): Tensor;
  export function expandDims(tensor: Tensor, axis: number): Tensor;
  export function reshape(tensor: Tensor, shape: number[]): Tensor;
  export function dispose(tensors: Tensor[]): void;
}
