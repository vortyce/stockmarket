import logging
import traceback
from app.db.session import SessionLocal
from app.services.options_monitoring_service import OptionsMonitoringService
from app.repositories.options_repo import OptionsRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_monitor_option_exits():
    db = SessionLocal()
    try:
        logger.info("Starting Monitor Option Exits job...")
        monitor_service = OptionsMonitoringService(db)
        repo = OptionsRepository(db)
        
        monitored = monitor_service.get_monitored_positions()
        
        exit_signals = [m for m in monitored if m["signal"] != "HOLD"]
        
        for item in exit_signals:
            logger.info(f"SIGNAL {item['signal']} for {item['ticker']} {item['option_symbol']}")
            # In Phase 6C, we just log/notify. In future phases, we might auto-close or alert deeper.
            # We could update the position with the signal
            pos = repo.get_position(item["position_id"])
            if pos:
                # Store signal in a new field or reason? 
                # Model doesn't have an 'exit_signal' yet, so we log it.
                pass
        
        logger.info(f"Monitor job finished. Processed {len(monitored)} positions. {len(exit_signals)} signals found.")
        
    except Exception as e:
        logger.error(f"Error in monitor_option_exits job: {e}")
        logger.error(traceback.format_exc())
    finally:
        db.close()

if __name__ == "__main__":
    run_monitor_option_exits()
