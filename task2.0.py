
import argparse
import os
from PIL import Image
import numpy as np


def swap_pixels(arr: np.ndarray) -> np.ndarray:
    """
    Swap pixel positions by flipping the image vertically and horizontally.
    This operation is its own inverse: applying it twice returns the original.
    """
    return arr[::-1, ::-1]  # reverse rows and columns


def xor_pixels(arr: np.ndarray, key: int) -> np.ndarray:
    """
    Apply XOR operation with the given key to every channel of every pixel.
    Also self-inverse: XOR with the same key again restores the original.
    """
    # Ensure type is uint8 to stay in [0, 255]
    return np.bitwise_xor(arr, key).astype(np.uint8)


def encrypt_array(arr: np.ndarray, key: int, mode: str) -> np.ndarray:
    """
    Encrypt the numpy array representing the image.
    mode: 'swap', 'math', or 'both'
    """
    if mode in ("math", "both"):
        arr = xor_pixels(arr, key)
    if mode in ("swap", "both"):
        arr = swap_pixels(arr)
    return arr


def decrypt_array(arr: np.ndarray, key: int, mode: str) -> np.ndarray:
    """
    Decrypt the numpy array representing the image.
    Since both operations are self-inverse, we apply in reverse order.
    """
    if mode in ("swap", "both"):
        arr = swap_pixels(arr)  # same function, same effect
    if mode in ("math", "both"):
        arr = xor_pixels(arr, key)
    return arr


def process_image(input_path: str, output_path: str, key: int, mode: str, operation: str):
    # Load image
    img = Image.open(input_path).convert("RGB")  # force RGB for simplicity
    arr = np.array(img)

    if operation == "encrypt":
        result_arr = encrypt_array(arr, key, mode)
    elif operation == "decrypt":
        result_arr = decrypt_array(arr, key, mode)
    else:
        raise ValueError("operation must be 'encrypt' or 'decrypt'")

    result_img = Image.fromarray(result_arr)
    result_img.save(output_path)
    print(f"{operation.capitalize()}ed image saved to: {output_path}")


def positive_int(value: str) -> int:
    try:
        ivalue = int(value)
        if not (0 <= ivalue <= 255):
            raise ValueError()
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError("Key must be an integer between 0 and 255")


def main():
    parser = argparse.ArgumentParser(
        description="Simple image encryption/decryption using pixel manipulation."
    )
    parser.add_argument("operation", choices=["encrypt", "decrypt"],
                        help="Whether to encrypt or decrypt the image.")
    parser.add_argument("input", help="Path to input image file.")
    parser.add_argument("output", help="Path to output image file.")
    parser.add_argument(
        "--key",
        type=positive_int,
        default=123,
        help="Numeric key (0–255) used for XOR operation. Default: 123"
    )
    parser.add_argument(
        "--mode",
        choices=["swap", "math", "both"],
        default="both",
        help="Which operations to use: swap pixels, math (XOR), or both. Default: both."
    )

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: input file '{args.input}' does not exist.")
        return

    process_image(args.input, args.output, args.key, args.mode, args.operation)


if __name__ == "__main__":
    main()
