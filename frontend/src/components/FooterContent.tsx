export function FooterContent() {
    const buildInfo = import.meta.env.VITE_APP_BUILD_INFO;
    return (
        <div>
            <p>
                Project <b>P&KU Website</b> by <b>P&KU Team</b>
                <br />
                build version {buildInfo}
                <br />
                <a href="https://beian.miit.gov.cn/" target="_blank" rel="noreferrer" style={{ color: 'inherit' }}>
                    京ICP备2022031972号-1
                </a>
            </p>
        </div>
    );
}
