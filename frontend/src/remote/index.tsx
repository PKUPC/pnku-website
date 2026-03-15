import './index.css';
import styles from './index.module.css';

// @ts-ignore
const { React } = window.exports;

export default function HelloWorld({ name }: { name?: string }) {
    return (
        <div className={styles.container}>
            <div className="flex items-center justify-center p-4">Hello {name ?? 'World'}</div>
        </div>
    );
}
