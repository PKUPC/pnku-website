import { Alert } from 'antd';
import { useContext } from 'react';

import { ThemeDropdown } from '@/app/(general)/setting/ThemeDropdown.tsx';
import FancyCard from '@/components/FancyCard';
import { InputWithLabel } from '@/components/InputWithLabel.tsx';
import { SiteSettingContext } from '@/logic/contexts.ts';

export function SettingPage() {
    const { usePuzzleList, setUsePuzzleList } = useContext(SiteSettingContext);
    return (
        <div className={'slim-container'}>
            <Alert
                type={'info'}
                showIcon={true}
                message={'设置保存在本地，清除浏览器数据或者切换浏览器会丢失设置。'}
                style={{ marginBottom: 16, marginTop: 16 }}
            />
            <FancyCard title="常规设置">
                <InputWithLabel
                    label={'选择主题（测试功能）'}
                    extra={'目前某些页面的颜色可能还没有适配好，仅限尝鲜用。'}
                >
                    <ThemeDropdown />
                </InputWithLabel>
                <br />
                <InputWithLabel
                    label={'谜题页显示谜题列表'}
                    extra={<>谜题页将显示该题所在谜题组的题目列表，也许有人觉得这样更方便。</>}
                >
                    <div className="join">
                        <input
                            className="join-item btn btn-sm"
                            type="radio"
                            name="options"
                            aria-label="不显示"
                            checked={usePuzzleList === 'off'}
                            onChange={(e) => {
                                if (e.target.checked) setUsePuzzleList('off');
                            }}
                        />
                        <input
                            className="join-item btn btn-sm"
                            type="radio"
                            name="options"
                            aria-label="总是显示"
                            checked={usePuzzleList === 'show'}
                            onChange={(e) => {
                                if (e.target.checked) setUsePuzzleList('show');
                            }}
                        />
                        <input
                            className="join-item btn btn-sm"
                            type="radio"
                            name="options"
                            aria-label="放入折叠侧栏"
                            checked={usePuzzleList === 'drawer'}
                            onChange={(e) => {
                                if (e.target.checked) setUsePuzzleList('drawer');
                            }}
                        />
                    </div>
                </InputWithLabel>
            </FancyCard>
        </div>
    );
}
