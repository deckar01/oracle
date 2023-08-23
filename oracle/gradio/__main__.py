from oracle.gradio.gui import demo


if __name__ == '__main__':
    demo.launch(
        server_port=8080,
        server_name='0.0.0.0',
        quiet=True,
        favicon_path='oracle/gradio/icon.png',
    )
