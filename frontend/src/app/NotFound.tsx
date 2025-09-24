import { Link } from 'react-router';

import styles from './NotFound.module.css';

export default function NotFound() {
    const size = 256;
    return (
        <div className={styles.container}>
            <div
                style={{
                    width: size,
                    height: size,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    overflow: 'hidden',
                }}
            >
                <img src={'/mion/images/BeiShangGuanCeZhe.webp'} style={{ width: '100%', height: '100%' }} alt="" />
            </div>
            <div className="settings">
                <div className="setting-body">
                    <h1>404</h1>
                    <h4>很抱歉！没有找到您要访问的页面！</h4>
                    <p>当前页面没有谜题</p>
                    <div>
                        <Link to="/home" title="返回首页" target="_self" rel="noopener noreferrer">
                            返回首页
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
