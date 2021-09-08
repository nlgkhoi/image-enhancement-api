from dependency_injector import containers, providers

#
# @author: anhlt
#
from enhance_service import EnhanceService
from image_downloader import ImageDownloader


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    downloader = providers.Singleton(
        ImageDownloader,
        num_threads=config.downloader.num_threads
    )
    enhance_service = providers.Singleton(
        EnhanceService,
        deblur_model_path=config.deblur_model_path,
        use_cpu=config.run_on_cpu,
        use_deblur_model=config.use_deblur_model,
        enhanced_output_only=config.enhanced_output_only,
    )
