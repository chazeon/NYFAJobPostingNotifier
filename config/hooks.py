from urlwatch.reporters import ReporterBase, TextReporter, logger, chunkstring, TelegramReporter
import itertools, requests


class TelegramReporter2(TelegramReporter):
    """Send a message using Telegram"""
    MAX_LENGTH = 4096

    __kind__ = 'telegram2'

    def get_details(self):

        for job_state in self.report.get_filtered_job_states(self.job_states):
            yield self._format_content(job_state)

    def submit(self):

        bot_token = self.config['bot_token']
        chat_ids = self.config['chat_id']
        chat_ids = [chat_ids] if isinstance(chat_ids, str) else chat_ids

        result = []

        for detail in self.get_details():
            if not detail:
                logger.debug('Not calling telegram API (no changes)')
                continue
            for chat_id in chat_ids:
                res = self.submitToTelegram(bot_token, chat_id, detail)
                if res.status_code != requests.codes.ok or res is None:
                    result.append(res)
        return result

    def submitToTelegram(self, bot_token, chat_id, text):
        logger.debug("Sending telegram request to chat id:'{0}'".format(chat_id))
        result = requests.post(
            "https://api.telegram.org/bot{0}/sendMessage".format(bot_token),
            data={"chat_id": chat_id, "text": text, "disable_web_page_preview": "true", "parse_mode": "HTML"})
        try:
            json_res = result.json()

            if (result.status_code == requests.codes.ok):
                logger.info("Telegram response: ok '{0}'. {1}".format(json_res['ok'], json_res['result']))
            else:
                logger.error("Telegram error: {0}".format(json_res['description']))
        except ValueError:
            logger.error(
                "Failed to parse telegram response. HTTP status code: {0}, content: {1}".format(result.status_code,
                                                                                                result.content))
        return result