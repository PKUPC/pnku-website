export function Cap({ text, width }: { text: string; width: number }) {
    return (
        <span
            className="capped-text"
            style={{
                maxWidth: width + 'px',
            }}
        >
            {text}
        </span>
    );
}
