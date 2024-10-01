import { Collapse, CollapseProps } from 'antd';

import styles from './CollapseCard.module.scss';

export default function CollapseCard(props: CollapseProps) {
    return (
        <div className={styles.collapseCard}>
            <Collapse {...props} />
        </div>
    );
}
